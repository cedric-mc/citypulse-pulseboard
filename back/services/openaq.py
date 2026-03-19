# ============================================================
# services/openaq.py — Service qualité de l'air
# Utilise OpenWeatherMap Air Pollution API
# Plus fiable que OpenAQ pour les données françaises
# Géolocalisation dynamique via OpenWeatherMap Geocoding API
# pour supporter toutes les villes, pas seulement les 5 hardcodées
# ============================================================

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Coordonnées GPS des villes connues — cache statique
# Évite un appel API de géolocalisation pour les villes fréquentes
CITY_COORDS_CACHE: dict[str, dict] = {
    "Paris":     {"lat": 48.8566, "lon": 2.3522},
    "Lyon":      {"lat": 45.7640, "lon": 4.8357},
    "Bordeaux":  {"lat": 44.8378, "lon": -0.5792},
    "Marseille": {"lat": 43.2965, "lon": 5.3698},
    "Lille":     {"lat": 50.6292, "lon": 3.0573},
    "Toulouse":  {"lat": 43.6047, "lon": 1.4442},
    "Nice":      {"lat": 43.7102, "lon": 7.2620},
    "Nantes":    {"lat": 47.2184, "lon": -1.5536},
    "Strasbourg":{"lat": 48.5734, "lon": 7.7521},
    "Rennes":    {"lat": 48.1173, "lon": -1.6778},
    "Angers":    {"lat": 47.4784, "lon": -0.5632},
    "Monaco":    {"lat": 43.7384, "lon": 7.4246},
}

# Correspondance AQI → label couleur pour le dashboard
AQI_LABELS = {
    1: {"label": "Bon",          "color": "green",  "advice": "Parfait pour les activités outdoor 🟢"},
    2: {"label": "Correct",      "color": "yellow", "advice": "Conditions acceptables 🟡"},
    3: {"label": "Modéré",       "color": "orange", "advice": "Évitez les efforts prolongés 🟠"},
    4: {"label": "Mauvais",      "color": "red",    "advice": "Évitez le sport intensif 🔴"},
    5: {"label": "Très mauvais", "color": "purple", "advice": "Restez à l'intérieur ⛔"},
}


# ============================================================
# Fonction : get_coords(city)
# Récupère les coordonnées GPS d'une ville
# Utilise le cache statique en priorité
# Fallback sur OpenWeatherMap Geocoding API pour les autres villes
# ============================================================
async def get_coords(city: str) -> dict:
    # Vérifie le cache statique en priorité
    if city in CITY_COORDS_CACHE:
        return CITY_COORDS_CACHE[city]

    # Géolocalisation dynamique via OpenWeatherMap Geocoding API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.openweathermap.org/geo/1.0/direct",
                params={
                    "q":     f"{city},FR",  # Priorité à la France
                    "limit": 1,
                    "appid": API_KEY,
                }
            )
            response.raise_for_status()
            data = response.json()

            if data:
                coords = {"lat": data[0]["lat"], "lon": data[0]["lon"]}
                # Stocke en cache pour les prochaines requêtes
                CITY_COORDS_CACHE[city] = coords
                return coords
        except Exception:
            pass

    # Fallback sur Paris si la géolocalisation échoue
    return CITY_COORDS_CACHE["Paris"]


# ============================================================
# Fonction : get_air_quality(city)
# Récupère AQI + PM2.5 + NO2 via OpenWeatherMap Air Pollution
# Supporte toutes les villes grâce à la géolocalisation dynamique
# ============================================================
async def get_air_quality(city: str):
    coords = await get_coords(city)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.openweathermap.org/data/2.5/air_pollution",
            params={
                "lat":   coords["lat"],
                "lon":   coords["lon"],
                "appid": API_KEY,
            }
        )

        response.raise_for_status()
        data = response.json()

        pollution  = data["list"][0]
        aqi        = pollution["main"]["aqi"]
        components = pollution["components"]
        aqi_info   = AQI_LABELS.get(aqi, AQI_LABELS[3])

        return {
            "city":   city,
            "aqi":    aqi,
            "label":  aqi_info["label"],
            "color":  aqi_info["color"],
            "advice": aqi_info["advice"],
            "pm25":   round(components.get("pm2_5", 0), 2),
            "no2":    round(components.get("no2",   0), 2),
            "o3":     round(components.get("o3",    0), 2),
            "co":     round(components.get("co",    0), 2),
        }