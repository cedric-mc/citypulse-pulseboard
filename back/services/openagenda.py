# ============================================================
# services/openagenda.py — Service événements OpenAgenda
# Récupère les 5 prochains événements publics d'une ville
# ============================================================

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAGENDA_API_KEY")
BASE_URL = "https://api.openagenda.com/v2"

# ============================================================
# Fonction : get_events(city)
# Récupère les 5 prochains événements publics d'une ville
# Retourne : nom, date, lieu, catégorie
# ============================================================
async def get_events(city: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/events",
            params={
                "key":            API_KEY,
                "oaq[city]":      city,       # Filtre par ville
                "size":           5,           # 5 événements max
                "sort":           "timingsWithFeatured.begin",  # Triés par date
                "relative[]":     "current",   # Événements en cours ou à venir
                "lang":           "fr"
            }
        )

        response.raise_for_status()
        data = response.json()

        # Formate chaque événement
        events = []
        for event in data.get("events", []):
            events.append({
                "title":    event.get("title", {}).get("fr", "Sans titre"),
                "date":     event.get("firstTiming", {}).get("begin", ""),
                "location": event.get("location", {}).get("name", ""),
                "city":     event.get("location", {}).get("city", city),
                "category": event.get("keywords", {}).get("fr", ["Événement"])[0] if event.get("keywords") else "Événement",
                "url":      f"https://openagenda.com/events/{event.get('slug', '')}"
            })

        return {
            "city":   city,
            "count":  len(events),
            "events": events
        }