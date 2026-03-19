# ============================================================
# services/openagenda.py — Service événements OpenAgenda
# Recherche dynamique multi-agendas par ville
# Étape 1 : GET /v2/agendas?search={city} → trouve les UIDs
#           en testant réellement chaque agenda pour ses events
#           à venir (plus fiable que eventsCount souvent à 0)
# Étape 2 : GET /v2/agendas/{UID}/events  → récupère les events
#           en parallèle sur tous les agendas, puis trie par date
# Filtre géographique par distance (Haversine) pour garantir
# que les events sont bien dans la ville demandée
# Filtre temporel en heure France (UTC+1) pour précision
# ============================================================

import httpx
import asyncio
import os
from datetime import datetime, timezone, timedelta
from math import radians, cos, sin, asin, sqrt
from dotenv import load_dotenv

load_dotenv()

API_KEY  = os.getenv("OPENAGENDA_API_KEY")
BASE_URL = "https://api.openagenda.com/v2"

# Cache local avec expiration 24h automatique
agenda_cache: dict[str, dict] = {}
CACHE_TTL_HOURS = 24

# Fuseau horaire France métropolitaine (UTC+1)
FRANCE_TZ = timezone(timedelta(hours=1))

# Rayon maximum en km pour qu'un event soit considéré
# comme appartenant à la ville demandée
# 30km = rayon raisonnable pour une grande ville
# Augmenté à 50km pour les petites villes moins denses
MAX_DISTANCE_KM = 30

# Coordonnées GPS des centres villes connus
# Utilisées pour le filtre de distance Haversine
CITY_CENTERS: dict[str, tuple[float, float]] = {
    "Paris":       (48.8566,  2.3522),
    "Lyon":        (45.7640,  4.8357),
    "Marseille":   (43.2965,  5.3698),
    "Toulouse":    (43.6047,  1.4442),
    "Nice":        (43.7102,  7.2620),
    "Bordeaux":    (44.8378, -0.5792),
    "Rennes":      (48.1173, -1.6778),
    "Nantes":      (47.2184, -1.5536),
    "Strasbourg":  (48.5734,  7.7521),
    "Lille":       (50.6292,  3.0573),
    "Angers":      (47.4784, -0.5632),
    "Monaco":      (43.7384,  7.4246),
    "Pau":         (43.2951, -0.3708),
    "Grenoble":    (45.1885,  5.7245),
    "Montpellier": (43.6108,  3.8767),
    "Dijon":       (47.3220,  5.0415),
    "Nancy":       (48.6921,  6.1844),
    "Brest":       (48.3904, -4.4861),
    "Tours":       (47.3941,  0.6848),
    "Rouen":       (49.4432,  1.0993),
}


def auth_headers() -> dict:
    return {"key": API_KEY}


# ============================================================
# Helpers : heure actuelle en France (UTC+1)
# ============================================================
def now_france() -> datetime:
    """Retourne l'heure actuelle en heure de France (UTC+1)"""
    return datetime.now(FRANCE_TZ)


def now_france_str() -> str:
    """Retourne l'heure actuelle France au format ISO pour OpenAgenda"""
    return now_france().strftime("%Y-%m-%dT%H:%M:%S.000Z")


# ============================================================
# Fonction : haversine(lat1, lon1, lat2, lon2)
# Calcule la distance en km entre deux points GPS
# Formule de Haversine — précise pour les courtes distances
# ============================================================
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance en km entre deux coordonnées GPS via Haversine"""
    R = 6371  # Rayon de la Terre en km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    return 2 * R * asin(sqrt(a))


# ============================================================
# Fonction : get_city_center(city, client)
# Récupère les coordonnées GPS du centre d'une ville
# Cache statique en priorité → Nominatim pour les autres
# ============================================================
async def get_city_center(city: str, client: httpx.AsyncClient) -> tuple[float, float] | None:
    # Cache statique en priorité — instantané
    if city in CITY_CENTERS:
        return CITY_CENTERS[city]

    # Géolocalisation via Nominatim pour les villes inconnues
    try:
        res = await client.get(
            f"https://nominatim.openstreetmap.org/search",
            params={
                "city":    city,
                "country": "France",
                "format":  "json",
                "limit":   1,
            },
            headers={"Accept-Language": "fr", "User-Agent": "PulseBoard/1.0"}
        )
        data = res.json()
        if data:
            coords = (float(data[0]["lat"]), float(data[0]["lon"]))
            # Stocke en cache statique pour les prochains appels
            CITY_CENTERS[city] = coords
            return coords
    except Exception:
        pass

    return None


# ============================================================
# Cache TTL — utilise total_seconds() et non .seconds
# ============================================================
def get_cached_uids(city: str) -> list[str] | None:
    entry = agenda_cache.get(city)
    if not entry:
        return None
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
# Cherche les UIDs des agendas les plus actifs pour une ville
# ============================================================
async def find_agenda_uids(city: str, client: httpx.AsyncClient, max_agendas: int = 3) -> list[str]:
    cached = get_cached_uids(city)
    if cached:
        return cached

    url = f"{BASE_URL}/agendas?search={city}&size=20&lang=fr"

    try:
        response = await client.get(url, headers=auth_headers())
        response.raise_for_status()
        data = response.json()

        agendas = data.get("agendas", [])
        if not agendas:
            return []

        async def count_upcoming_events(agenda_uid: str) -> tuple[str, int]:
            now_str = now_france_str()
            test_url = (
                f"{BASE_URL}/agendas/{agenda_uid}/events"
                f"?size=1"
                f"&relative[]=upcoming"
                f"&relative[]=current"
                f"&timings[gte]={now_str}"
                f"&location[city]={city}"
            )
            try:
                r = await client.get(test_url, headers=auth_headers())
                r.raise_for_status()
                total = r.json().get("total", 0)
                return agenda_uid, total
            except Exception:
                return agenda_uid, 0

        all_uids = [str(a["uid"]) for a in agendas]
        counts = await asyncio.gather(*[count_upcoming_events(uid) for uid in all_uids])
        counts_sorted = sorted(counts, key=lambda x: x[1], reverse=True)
        uids = [uid for uid, count in counts_sorted[:max_agendas] if count > 0]

        if not uids:
            print(f"[AGENDA] Aucun event dans {city} exactement — fallback sans filtre ville")
            uids = all_uids[:max_agendas]

        set_cached_uids(city, uids)
        return uids

    except Exception as e:
        print(f"Erreur find_agenda_uids({city}): {e}")
        return []


# ============================================================
# Fonction : fetch_agenda_events(uid, city, client)
# Récupère les prochains événements d'un agenda spécifique
# Filtre par :
#   - ville exacte via location[city]
#   - heure France (UTC+1) via timings[gte]
#   - nextTiming pour les events récurrents
#   - distance Haversine ≤ MAX_DISTANCE_KM du centre ville
#     pour éliminer les events hors zone géographique
# ============================================================
async def fetch_agenda_events(uid: str, city: str, client: httpx.AsyncClient) -> list[dict]:
    now_str = now_france_str()

    # Récupère le centre ville pour le filtre de distance
    city_center = await get_city_center(city, client)

    url_with_city = (
        f"{BASE_URL}/agendas/{uid}/events"
        f"?size=10"
        f"&relative[]=upcoming"
        f"&relative[]=current"
        f"&timings[gte]={now_str}"
        f"&location[city]={city}"
        f"&sort=timings.asc"
        f"&monolingual=fr"
    )

    url_without_city = (
        f"{BASE_URL}/agendas/{uid}/events"
        f"?size=10"
        f"&relative[]=upcoming"
        f"&relative[]=current"
        f"&timings[gte]={now_str}"
        f"&sort=timings.asc"
        f"&monolingual=fr"
    )

    def parse_events(data: dict, strict_distance: bool = True) -> list[dict]:
        events = []
        for event in data.get("events", []):
            event_uid  = event.get("uid", "")
            location   = event.get("location", {}) or {}

            # --------------------------------------------------------
            # Filtre de distance Haversine
            # Si l'event a des coordonnées GPS et qu'on a le centre ville
            # on vérifie qu'il est bien dans le rayon MAX_DISTANCE_KM
            # Sinon on accepte l'event (pas de coords = pas de filtrage)
            # --------------------------------------------------------
            event_lat = location.get("latitude")
            event_lon = location.get("longitude")

            if strict_distance and city_center and event_lat and event_lon:
                distance = haversine(
                    city_center[0], city_center[1],
                    float(event_lat), float(event_lon)
                )
                if distance > MAX_DISTANCE_KM:
                    # Event trop loin — on l'ignore
                    continue

            # nextTiming = prochaine occurrence à venir (events récurrents)
            # firstTiming = première occurrence historique (peut être passée)
            next_timing  = event.get("nextTiming", {}) or {}
            first_timing = event.get("firstTiming", {}) or {}
            date_begin   = next_timing.get("begin") or first_timing.get("begin", "")

            # Vérifie que l'event est bien dans le futur en heure France
            if date_begin:
                try:
                    dt = datetime.fromisoformat(date_begin.replace("Z", "+00:00"))
                    if dt < now_france():
                        continue
                except Exception:
                    pass

            events.append({
                "title":       event.get("title", "Sans titre"),
                "description": event.get("description", ""),
                "date":        date_begin,
                # Coordonnées GPS réelles de l'event
                # Utilisées par MapSection pour placer les marqueurs
                "lat":         float(event_lat) if event_lat else None,
                "lon":         float(event_lon) if event_lon else None,
                "location":    location.get("name", ""),
                "address":     location.get("address", ""),
                "city":        city,
                "category":    (
                    event.get("keywords", ["Événement"])[0]
                    if event.get("keywords") else "Événement"
                ),
                # external_id combine agenda_uid + event_uid pour unicité
                "external_id": f"{uid}_{event_uid}",
                # URL directe vers la page de l'événement sur OpenAgenda
                "url":         f"https://openagenda.com/agendas/{uid}/events/{event_uid}"
            })
        return events

    try:
        # Essai 1 — avec filtre ville exacte + distance stricte
        response = await client.get(url_with_city, headers=auth_headers())
        response.raise_for_status()
        events = parse_events(response.json(), strict_distance=True)

        # Si aucun résultat → fallback sans filtre ville
        # mais on garde le filtre de distance
        if not events:
            print(f"[AGENDA] Aucun event pour {city} avec filtre ville — fallback sans filtre")
            response = await client.get(url_without_city, headers=auth_headers())
            response.raise_for_status()
            events = parse_events(response.json(), strict_distance=True)

        # Si toujours rien → fallback total sans filtre distance
        # pour les petites villes avec peu d'events géolocalisés
        if not events:
            print(f"[AGENDA] Fallback total pour {city} — sans filtre distance")
            response = await client.get(url_without_city, headers=auth_headers())
            response.raise_for_status()
            events = parse_events(response.json(), strict_distance=False)

        return events

    except Exception as e:
        print(f"Erreur fetch_agenda_events({uid}, {city}): {e}")
        return []


# ============================================================
# Fonction : get_events(city)
# Récupère les prochains événements pour une ville
# Triés par date et heure France — les plus proches d'abord
# ============================================================
async def get_events(city: str):
    async with httpx.AsyncClient() as client:
        uids = await find_agenda_uids(city, client)

        if not uids:
            return {
                "city":    city,
                "count":   0,
                "source":  "error",
                "message": f"Aucun agenda trouvé pour {city}",
                "events":  []
            }

        results = await asyncio.gather(
            *[fetch_agenda_events(uid, city, client) for uid in uids]
        )

        all_events = [event for agenda_events in results for event in agenda_events]

        # Tri par date et heure France — les plus proches d'abord
        def sort_key(e: dict) -> datetime:
            try:
                return datetime.fromisoformat(
                    (e["date"] or "9999").replace("Z", "+00:00")
                )
            except Exception:
                return datetime.max.replace(tzinfo=timezone.utc)

        all_events.sort(key=sort_key)

        # Dédoublonnage par titre
        seen = set()
        unique_events = []
        for event in all_events:
            key = event["title"].lower().strip()
            if key not in seen:
                seen.add(key)
                unique_events.append(event)

        return {
            "city":   city,
            "count":  len(unique_events),
            "source": "live",
            "events": unique_events
        }