# ============================================================
# services/openagenda.py — Service événements OpenAgenda
# Recherche dynamique multi-agendas par ville
# Étape 1 : GET /v2/agendas?search={city} → trouve les UIDs
#           en testant réellement chaque agenda pour ses events
#           à venir (plus fiable que eventsCount souvent à 0)
# Étape 2 : GET /v2/agendas/{UID}/events  → récupère les events
#           en parallèle sur tous les agendas, puis trie par date
# ============================================================

import httpx
import asyncio
import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAGENDA_API_KEY")
BASE_URL = "https://api.openagenda.com/v2"

# Cache local avec expiration 24h automatique
agenda_cache: dict[str, dict] = {}
CACHE_TTL_HOURS = 24


# ============================================================
# Helpers : headers d'authentification
# La clé passe en header (recommandé par la doc officielle)
# plutôt qu'en query string pour éviter les fuites dans les logs
# ============================================================
def auth_headers() -> dict:
    return {"key": API_KEY}


# ============================================================
# Helpers : gestion du cache avec expiration 24h
# Correction du bug : utilise total_seconds() au lieu de seconds
# seconds retourne seulement la partie secondes (0-59)
# total_seconds() retourne la durée totale en secondes
# ============================================================
def get_cached_uids(city: str) -> list[str] | None:
    entry = agenda_cache.get(city)
    if not entry:
        return None
    # ← FIX : total_seconds() au lieu de .seconds pour éviter
    # que le cache ne soit jamais expiré après 1h
    age_hours = (datetime.now(timezone.utc) - entry["cached_at"]).total_seconds() / 3600
    if age_hours > CACHE_TTL_HOURS:
        del agenda_cache[city]
        return None
    return entry["uids"]

def set_cached_uids(city: str, uids: list[str]) -> None:
    agenda_cache[city] = {
        "uids":      uids,
        "cached_at": datetime.now(timezone.utc)
    }


# ============================================================
# Fonction : find_agenda_uids(city)
# Cherche dynamiquement les UIDs des agendas les plus actifs
# pour une ville donnée en testant réellement chaque agenda
# Trie par nombre réel d'events à venir (pas eventsCount)
# ============================================================
async def find_agenda_uids(city: str, client: httpx.AsyncClient, max_agendas: int = 3) -> list[str]:
    # Si déjà en cache et pas expiré → retourne directement
    cached = get_cached_uids(city)
    if cached:
        return cached

    # Recherche les agendas de la ville — size=20 pour plus de choix
    url = f"{BASE_URL}/agendas?search={city}&size=20&lang=fr"

    try:
        response = await client.get(url, headers=auth_headers())
        response.raise_for_status()
        data = response.json()

        agendas = data.get("agendas", [])
        if not agendas:
            return []

        # --------------------------------------------------------
        # Teste chaque agenda en parallèle pour compter ses events
        # à venir réels — eventsCount est souvent à 0 et non fiable
        # --------------------------------------------------------
        async def count_upcoming_events(agenda_uid: str) -> tuple[str, int]:
            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            test_url = (
                f"{BASE_URL}/agendas/{agenda_uid}/events"
                f"?size=1"
                f"&relative[]=upcoming"
                f"&relative[]=current"
                f"&timings[gte]={now_str}"
            )
            try:
                r = await client.get(test_url, headers=auth_headers())
                r.raise_for_status()
                total = r.json().get("total", 0)
                return agenda_uid, total
            except Exception:
                return agenda_uid, 0

        # Lance les tests en parallèle sur tous les agendas trouvés
        all_uids = [str(a["uid"]) for a in agendas]
        counts = await asyncio.gather(*[count_upcoming_events(uid) for uid in all_uids])

        # Trie par nombre réel d'events à venir (les plus actifs en premier)
        counts_sorted = sorted(counts, key=lambda x: x[1], reverse=True)

        # Garde les N agendas avec le plus d'events réels
        uids = [uid for uid, count in counts_sorted[:max_agendas] if count > 0]

        # Fallback — si aucun agenda n'a d'events, prend les 3 premiers quand même
        if not uids:
            uids = all_uids[:max_agendas]

        # Stocke en cache pour les prochaines requêtes
        set_cached_uids(city, uids)

        # DEBUG — affiche les agendas sélectionnés avec leur nombre réel d'events
        print(f"=== AGENDAS SÉLECTIONNÉS POUR {city} ===")
        for uid, count in counts_sorted[:max_agendas]:
            print(f"  - uid: {uid}, events à venir réels: {count}")
        print("==========================================")

        return uids

    except Exception as e:
        print(f"Erreur find_agenda_uids({city}): {e}")
        return []


# ============================================================
# Fonction : fetch_agenda_events(uid, city, client)
# Récupère les prochains événements d'un agenda spécifique
# timings[gte] = maintenant → exclut les horaires déjà passés
# Utilise nextTiming pour les events récurrents — plus fiable
# que firstTiming qui pointe vers la première occurrence historique
# ============================================================
async def fetch_agenda_events(uid: str, city: str, client: httpx.AsyncClient) -> list[dict]:
    now     = datetime.now(timezone.utc)
    now_str = now.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    url = (
        f"{BASE_URL}/agendas/{uid}/events"
        f"?size=10"
        f"&relative[]=upcoming"
        f"&relative[]=current"
        f"&timings[gte]={now_str}"
        f"&sort=timings.asc"
        f"&monolingual=fr"
    )

    try:
        response = await client.get(url, headers=auth_headers())
        response.raise_for_status()
        data = response.json()

        # DEBUG — affiche le premier événement brut pour vérifier les champs
        if data.get("events"):
            print(f"=== DEBUG EVENT ({city} / agenda {uid}) ===")
            print(data["events"][0])
            print("============================================")

        events = []
        for event in data.get("events", []):
            event_uid = event.get("uid", "")

            # --------------------------------------------------------
            # Utilise nextTiming en priorité sur firstTiming
            # nextTiming = prochaine occurrence à venir (events récurrents)
            # firstTiming = première occurrence historique (peut être en 2025)
            # Fallback sur firstTiming si nextTiming absent
            # --------------------------------------------------------
            next_timing  = event.get("nextTiming", {}) or {}
            first_timing = event.get("firstTiming", {}) or {}
            date_begin   = next_timing.get("begin") or first_timing.get("begin", "")

            events.append({
                "title":       event.get("title", "Sans titre"),
                "description": event.get("description", ""),
                "date":        date_begin,
                "location":    event.get("location", {}).get("name", ""),
                "city":        city,
                "category":    (
                    event.get("keywords", ["Événement"])[0]
                    if event.get("keywords") else "Événement"
                ),
                # external_id combine agenda_uid + event_uid pour garantir
                # l'unicité même si le même event apparaît dans plusieurs agendas
                "external_id": f"{uid}_{event_uid}",
                # URL directe vers la page de l'événement sur OpenAgenda
                "url":         f"https://openagenda.com/agendas/{uid}/events/{event_uid}"
            })

        return events

    except Exception as e:
        print(f"Erreur fetch_agenda_events({uid}, {city}): {e}")
        return []


# ============================================================
# Fonction : get_events(city)
# Récupère les prochains événements pour une ville
# Fonctionne pour toutes les villes de façon uniforme :
#   - Trouve les N agendas avec le plus d'events réels
#   - Récupère leurs events en parallèle
#   - Fusionne, dédoublonne par titre, trie par date
# ============================================================
async def get_events(city: str):
    async with httpx.AsyncClient() as client:

        # Étape 1 — Trouve les UIDs des agendas les plus actifs
        uids = await find_agenda_uids(city, client)

        if not uids:
            return {
                "city":    city,
                "count":   0,
                "source":  "error",
                "message": f"Aucun agenda trouvé pour {city}",
                "events":  []
            }

        # Étape 2 — Récupère les événements en parallèle sur tous les agendas
        results = await asyncio.gather(
            *[fetch_agenda_events(uid, city, client) for uid in uids]
        )

        # Fusionne tous les événements de tous les agendas
        all_events = [event for agenda_events in results for event in agenda_events]

        # Tri final par date croissante (les plus proches d'abord)
        all_events.sort(key=lambda e: e["date"] or "9999")

        # Dédoublonnage par titre pour éviter les doublons
        # d'events récurrents insérés depuis plusieurs agendas
        seen = set()
        unique_events = []
        for event in all_events:
            key = event["title"].lower().strip()
            if key not in seen:
                seen.add(key)
                unique_events.append(event)

        # Limite à 5 events max comme demandé
        top_events = unique_events[:5]

        return {
            "city":   city,
            "count":  len(top_events),
            "source": "live",
            "events": top_events
        }