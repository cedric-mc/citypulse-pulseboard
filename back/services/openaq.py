# ============================================================
# services/openaq.py — Service qualité de l'air
# Utilise OpenWeatherMap Air Pollution API
# Plus fiable que OpenAQ pour les données françaises
# ============================================================

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Coordonnées GPS des villes du projet
CITY_COORDS = {
    "Paris":     {"lat": 48.8566, "lon": 2.3522},
    "Lyon":      {"lat": 45.7640, "lon": 4.8357},
    "Bordeaux":  {"lat": 44.8378, "lon": -0.5792},
    "Marseille": {"lat": 43.2965, "lon": 5.3698},
    "Lille":     {"lat": 50.6292, "lon": 3.0573},
}

# Correspondance AQI → label couleur pour le dashboard
AQI_LABELS = {
    1: {"label": "Bon",           "color": "green",  "advice": "Parfait pour les activités outdoor 🟢"},
    2: {"label": "Correct",       "color": "yellow", "advice": "Conditions acceptables 🟡"},
    3: {"label": "Modéré",        "color": "orange", "advice": "Évitez les efforts prolongés 🟠"},
    4: {"label": "Mauvais",       "color": "red",    "advice": "Évitez le sport intensif 🔴"},
    5: {"label": "Très mauvais",  "color": "purple", "advice": "Restez à l'intérieur ⛔"},
}

# ============================================================
# Fonction : get_air_quality(city)
# Récupère AQI + PM2.5 + NO2 via OpenWeatherMap Air Pollution
# ============================================================
async def get_air_quality(city: str):
    # Récupère les coordonnées GPS de la ville
    coords = CITY_COORDS.get(city, CITY_COORDS["Paris"])

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.openweathermap.org/data/2.5/air_pollution",
            params={
                "lat":   coords["lat"],
                "lon":   coords["lon"],
                "appid": API_KEY
            }
        )

        response.raise_for_status()
        data = response.json()

        # Extrait les données de pollution
        pollution = data["list"][0]
        aqi       = pollution["main"]["aqi"]         # 1 à 5
        components = pollution["components"]

        # Récupère le label et conseil associés à l'AQI
        aqi_info = AQI_LABELS.get(aqi, AQI_LABELS[3])

        return {
            "city":   city,
            "aqi":    aqi,
            "label":  aqi_info["label"],
            "color":  aqi_info["color"],
            "advice": aqi_info["advice"],
            "pm25":   round(components.get("pm2_5", 0), 2),   # µg/m³
            "no2":    round(components.get("no2",   0), 2),   # µg/m³
            "o3":     round(components.get("o3",    0), 2),   # µg/m³
            "co":     round(components.get("co",    0), 2),   # µg/m³
        }