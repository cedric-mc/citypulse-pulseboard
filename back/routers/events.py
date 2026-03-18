# ============================================================
# routers/events.py — Endpoints événements
# Gère les routes liées aux événements via OpenAgenda
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.data_pipeline import refresh_city_data, get_events_for_city, events_to_response

router = APIRouter()

# ============================================================
# GET /api/events/{city}
# Retourne les 5 prochains événements publics d'une ville
# Exemple : GET /api/events/Paris
# ============================================================
@router.get("/events/{city}")
async def events_list(city: str, db: Session = Depends(get_db)):
    try:
        await refresh_city_data(db, city)
        rows = get_events_for_city(db, city)
        return events_to_response(rows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))