# ============================================================
# routers/weather.py — Endpoints météo
# Gère les routes liées à la météo via OpenWeatherMap
# Synchronise automatiquement les données à la volée
# Stratégie : lance la sync en arrière-plan sans bloquer
# Si aucune donnée en BDD → attend la sync complète (1ère fois)
# ============================================================

import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.openweather import get_forecast
from services.data_pipeline import get_latest_weather, weather_to_response, refresh_city_data

router = APIRouter()


@router.get("/weather/{city}")
async def weather_current(city: str, db: Session = Depends(get_db)):
    try:
        row = get_latest_weather(db, city)

        if not row:
            # Première fois pour cette ville — on attend la sync complète
            # avant de répondre car rien n'est encore en BDD
            await refresh_city_data(db, city)
            row = get_latest_weather(db, city)
        else:
            # Données déjà en BDD — on répond immédiatement
            # et on lance la sync en arrière-plan pour les mettre à jour
            asyncio.create_task(refresh_city_data(db, city))

        if not row:
            raise HTTPException(status_code=404, detail="Aucune donnée météo en base")
        return weather_to_response(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forecast/{city}")
async def weather_forecast(city: str, db: Session = Depends(get_db)):
    try:
        data = await get_forecast(city)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))