# ============================================================
# routers/score.py — Endpoint score urbain
# Calcule le score global d'une ville depuis les données en BDD
# Synchronise automatiquement les données à la volée
# Stratégie : lance la sync en arrière-plan sans bloquer
# Si aucune donnée en BDD → attend la sync complète (1ère fois)
# ============================================================

import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.data_pipeline import (
    get_events_for_city,
    get_latest_air_quality,
    get_latest_weather,
    score_to_response,
    refresh_city_data,
)

router = APIRouter()


@router.get("/score/{city}")
async def urban_score(city: str, db: Session = Depends(get_db)):
    try:
        weather = get_latest_weather(db, city)
        air     = get_latest_air_quality(db, city)

        if not weather or not air:
            # Première fois pour cette ville — on attend la sync complète
            # car le score a besoin de météo ET qualité de l'air en BDD
            await refresh_city_data(db, city)
            weather = get_latest_weather(db, city)
            air     = get_latest_air_quality(db, city)
        else:
            # Données déjà en BDD — on répond immédiatement
            # et on lance la sync en arrière-plan pour les mettre à jour
            asyncio.create_task(refresh_city_data(db, city))

        if not weather or not air:
            raise HTTPException(
                status_code=404,
                detail="Données insuffisantes en base pour calculer le score"
            )

        events = get_events_for_city(db, city)
        return score_to_response(city, weather, air, events)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))