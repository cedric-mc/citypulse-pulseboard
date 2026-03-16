# ============================================================
# routers/score.py — Endpoint score urbain
# Calcule le score global d'une ville sur 100
# Score = météo (40%) + qualité air (40%) + événements (20%)
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.openweather import get_weather
from services.openaq import get_air_quality
from services.openagenda import get_events

router = APIRouter()

# ============================================================
# Fonction utilitaire — calcule le score météo (0-100)
# Basé sur température, humidité et vitesse du vent
# ============================================================
def calculate_weather_score(weather: dict) -> float:
    score = 100.0

    # Pénalité température (idéale entre 15°C et 25°C)
    temp = weather.get("temperature", 20)
    if temp < 0 or temp > 35:
        score -= 40
    elif temp < 10 or temp > 30:
        score -= 20
    elif temp < 15 or temp > 25:
        score -= 10

    # Pénalité humidité (idéale entre 30% et 60%)
    humidity = weather.get("humidity", 50)
    if humidity > 80:
        score -= 20
    elif humidity > 70:
        score -= 10

    # Pénalité vent (idéal < 20 km/h)
    wind = weather.get("wind_speed", 0)
    if wind > 50:
        score -= 30
    elif wind > 30:
        score -= 15
    elif wind > 20:
        score -= 5

    return max(0, min(100, score))  # Clamp entre 0 et 100

# ============================================================
# Fonction utilitaire — calcule le score qualité air (0-100)
# Basé sur l'indice AQI (1=Bon → 5=Très mauvais)
# ============================================================
def calculate_air_score(air: dict) -> float:
    aqi = air.get("aqi", 3)
    scores = {1: 100, 2: 75, 3: 50, 4: 25, 5: 10}
    return scores.get(aqi, 50)

# ============================================================
# Fonction utilitaire — calcule le score événements (0-100)
# Plus il y a d'événements, plus le score est élevé
# ============================================================
def calculate_events_score(events: dict) -> float:
    count = len(events.get("events", []))
    if count == 0:
        return 20
    elif count == 1:
        return 40
    elif count == 2:
        return 60
    elif count >= 3:
        return 100
    return 20

# ============================================================
# GET /api/score/{city}
# Retourne le score urbain global + détail des sous-scores
# Exemple : GET /api/score/Paris
# ============================================================
@router.get("/score/{city}")
async def urban_score(city: str, db: Session = Depends(get_db)):
    try:
        # Récupère les données des 3 sources
        weather = await get_weather(city)
        air     = await get_air_quality(city)
        events  = await get_events(city)

        # Calcule les sous-scores
        weather_score = calculate_weather_score(weather)
        air_score     = calculate_air_score(air)
        events_score  = calculate_events_score(events)

        # Score global pondéré : météo 40% + air 40% + events 20%
        global_score = (
            weather_score * 0.4 +
            air_score     * 0.4 +
            events_score  * 0.2
        )

        return {
            "city": city,
            "score": round(global_score, 1),
            "details": {
                "weather_score": round(weather_score, 1),
                "air_score":     round(air_score, 1),
                "events_score":  round(events_score, 1),
            },
            "ponderation": {
                "weather": "40%",
                "air":     "40%",
                "events":  "20%"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))