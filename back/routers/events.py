# ============================================================
# routers/events.py — Endpoints événements
# Gère les routes liées aux événements via OpenAgenda
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.openagenda import get_events

router = APIRouter()

# ============================================================
# GET /api/events/{city}
# Retourne les 5 prochains événements publics d'une ville
# Exemple : GET /api/events/Paris
# ============================================================
@router.get("/events/{city}")
async def events_list(city: str, db: Session = Depends(get_db)):
    try:
        data = await get_events(city)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))