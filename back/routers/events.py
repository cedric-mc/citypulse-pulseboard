# ============================================================
# routers/events.py — Endpoints événements
# Gère les routes liées aux événements via OpenAgenda
# Synchronise automatiquement les données à la volée
# Stratégie : lance la sync en arrière-plan sans bloquer
# Si aucune donnée en BDD → attend la sync complète (1ère fois)
# ============================================================

import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.data_pipeline import get_events_for_city, events_to_response, refresh_city_data

router = APIRouter()


@router.get("/events/{city}")
async def events_list(city: str, db: Session = Depends(get_db)):
    try:
        rows = get_events_for_city(db, city)

        if not rows:
            # Première fois pour cette ville — on attend la sync complète
            # avant de répondre car rien n'est encore en BDD
            await refresh_city_data(db, city)
            rows = get_events_for_city(db, city)
        else:
            # Données déjà en BDD — on répond immédiatement
            # et on lance la sync en arrière-plan pour les mettre à jour
            asyncio.create_task(refresh_city_data(db, city))

        return events_to_response(rows)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))