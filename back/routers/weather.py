# ============================================================
# routers/weather.py — Endpoints météo
# Gère les routes liées à la météo via OpenWeatherMap
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.openweather import get_weather, get_forecast

# Crée le router — sera inclus dans main.py
router = APIRouter()

# ============================================================
# GET /api/weather/{city}
# Retourne la météo actuelle d'une ville
# Exemple : GET /api/weather/Paris
# ============================================================
@router.get("/weather/{city}")
async def weather_current(city: str, db: Session = Depends(get_db)):
    try:
        data = await get_weather(city)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# GET /api/forecast/{city}
# Retourne les prévisions météo sur 24h (par pas de 3h)
# Exemple : GET /api/forecast/Paris
# ============================================================
@router.get("/forecast/{city}")
async def weather_forecast(city: str, db: Session = Depends(get_db)):
    try:
        data = await get_forecast(city)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))