# ============================================================
# services/openagenda.py — Service événements OpenAgenda
# Option 2 : Recherche dynamique de l'agendaUID par ville
# Étape 1 : GET /v2/agendas?search={city} → trouve l'UID
# Étape 2 : GET /v2/agendas/{UID}/events  → récupère les events
# ============================================================

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAGENDA_API_KEY")
BASE_URL = "https://api.openagenda.com/v2"

# Cache local pour éviter de chercher l'UID à chaque requête
# Une fois trouvé, on le stocke en mémoire
agenda_cache = {}

# ============================================================
# Fonction : find_agenda_uid(city)
# Cherche dynamiquement l'UID de l'agenda officiel d'une ville
# ============================================================
async def find_agenda_uid(city: str, client: httpx.AsyncClient) -> str | None:
    # Si déjà en cache → retourne directement
    if city in agenda_cache:
        return agenda_cache[city]

    # Recherche l'agenda de la ville
    url = (
        f"{BASE_URL}/agendas"
        f"?key={API_KEY}"
        f"&search={city}"
        f"&size=5"
        f"&lang=fr"
    )

    response = await client.get(url)
    response.raise_for_status()
    data = response.json()

    agendas = data.get("agendas", [])

    if not agendas:
        return None

    # Prend le premier agenda trouvé
    uid = str(agendas[0].get("uid"))

    # Stocke en cache pour les prochaines requêtes
    agenda_cache[city] = uid

    return uid

# ============================================================
# Fonction : get_events(city)
# Récupère les 5 prochains événements d'une ville
# Cherche d'abord l'UID de l'agenda puis récupère les events
# ============================================================
async def get_events(city: str):
    async with httpx.AsyncClient() as client:

        # Étape 1 — Trouve l'UID de l'agenda de la ville
        agenda_uid = await find_agenda_uid(city, client)

        if not agenda_uid:
            # Aucun agenda trouvé pour cette ville
            return {
                "city":    city,
                "count":   0,
                "source":  "error",
                "message": f"Aucun agenda trouvé pour {city}",
                "events":  []
            }

        # Étape 2 — Récupère les événements de cet agenda
        url = (
            f"{BASE_URL}/agendas/{agenda_uid}/events"
            f"?key={API_KEY}"
            f"&size=5"
            f"&relative[]=upcoming"
            f"&lang=fr"
        )

        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

        # Formate chaque événement
        events = []
        for event in data.get("events", []):
            events.append({
                "title":    event.get("title", {}).get("fr", "Sans titre"),
                "date":     event.get("firstTiming", {}).get("begin", ""),
                "location": event.get("location", {}).get("name", ""),
                "city":     city,
                "category": event.get("keywords", {}).get("fr", ["Événement"])[0] if event.get("keywords") else "Événement",
                "url":      f"https://openagenda.com/events/{event.get('slug', '')}"
            })

        return {
            "city":      city,
            "count":     len(events),
            "source":    "live",
            "agenda_uid": agenda_uid,  # Utile pour debug
            "events":    events
        }