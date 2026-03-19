# ============================================================
# routers/air.py — Endpoints qualité de l'air
# Gère les routes liées à la qualité de l'air via OpenAQ
# Synchronise automatiquement les données à la volée
# Stratégie : lance la sync en arrière-plan sans bloquer
# Si aucune donnée en BDD → attend la sync complète (1ère fois)
# ============================================================

import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.data_pipeline import get_latest_air_quality, air_to_response, refresh_city_data

router = APIRouter()


@router.get("/air/{city}")
async def air_quality(city: str, db: Session = Depends(get_db)):
    try:
        row = get_latest_air_quality(db, city)

        if not row:
            # Première fois pour cette ville — on attend la sync complète
            # avant de répondre car rien n'est encore en BDD
            await refresh_city_data(db, city)
            row = get_latest_air_quality(db, city)
        else:
            # Données déjà en BDD — on répond immédiatement
            # et on lance la sync en arrière-plan pour les mettre à jour
            asyncio.create_task(refresh_city_data(db, city))

        if not row:
            raise HTTPException(status_code=404, detail="Aucune donnée qualité de l'air en base")
        return air_to_response(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))