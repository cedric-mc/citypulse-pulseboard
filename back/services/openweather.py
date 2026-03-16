# ============================================================
# services/openweather.py — Service OpenWeatherMap
# Gère tous les appels à l'API OpenWeatherMap
# Météo actuelle + prévisions 24h + qualité de l'air
# ============================================================

import httpx
import os
from dotenv import load_dotenv

# Charge les variables d'environnement du .env
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"

# ============================================================
# Fonction : get_weather(city)
# Récupère la météo actuelle d'une ville
# Retourne : température, humidité, vent, description, icône
# ============================================================
async def get_weather(city: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/weather",
            params={
                "q": city,           # Nom de la ville
                "appid": API_KEY,    # Clé API
                "units": "metric",   # Celsius (sinon Kelvin par défaut)
                "lang": "fr"         # Descriptions en français
            }
        )

        # Vérifie que la requête a réussi
        response.raise_for_status()
        data = response.json()

        # Retourne uniquement les données utiles pour le dashboard
        return {
            "city":        city,
            "temperature": round(data["main"]["temp"], 1),        # °C
            "feels_like":  round(data["main"]["feels_like"], 1),  # °C ressenti
            "humidity":    data["main"]["humidity"],               # %
            "wind_speed":  round(data["wind"]["speed"] * 3.6, 1), # m/s → km/h
            "description": data["weather"][0]["description"],     # ex: "ciel dégagé"
            "icon":        data["weather"][0]["icon"],             # ex: "01d"
            "icon_url":    f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
        }

# ============================================================
# Fonction : get_forecast(city)
# Récupère les prévisions météo sur 24h (8 points x 3h)
# Retourne : liste de prévisions avec heure + température
# ============================================================
async def get_forecast(city: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/forecast",
            params={
                "q":     city,
                "appid": API_KEY,
                "units": "metric",
                "lang":  "fr",
                "cnt":   8    # 8 points = 24h par pas de 3h
            }
        )

        response.raise_for_status()
        data = response.json()

        # Formate chaque point de prévision
        forecasts = []
        for item in data["list"]:
            forecasts.append({
                "time":        item["dt_txt"],                          # ex: "2026-03-16 12:00:00"
                "temperature": round(item["main"]["temp"], 1),          # °C
                "feels_like":  round(item["main"]["feels_like"], 1),    # °C ressenti
                "humidity":    item["main"]["humidity"],                 # %
                "description": item["weather"][0]["description"],       # description météo
                "icon":        item["weather"][0]["icon"],               # code icône
                "icon_url":    f"https://openweathermap.org/img/wn/{item['weather'][0]['icon']}@2x.png"
            })

        return {
            "city":      city,
            "forecasts": forecasts
        }