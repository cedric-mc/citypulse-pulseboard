# ============================================================
# routers/score.py — Endpoint score urbain
# Calcule le score global d'une ville depuis les donnees en BDD
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from services.data_pipeline import (
    get_events_for_city,
    get_latest_air_quality,
    get_latest_weather,
    refresh_city_data,
    score_to_response,
)

router = APIRouter()


@router.get("/score/{city}")
async def urban_score(city: str, db: Session = Depends(get_db)):
    try:
        await refresh_city_data(db, city)

        weather = get_latest_weather(db, city)
        air = get_latest_air_quality(db, city)
        events = get_events_for_city(db, city)

        if not weather or not air:
            raise HTTPException(status_code=404, detail="Donnees insuffisantes en base pour calculer le score")

        return score_to_response(city, weather, air, events)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
