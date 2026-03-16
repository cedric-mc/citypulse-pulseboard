# ============================================================
# routers/air.py — Endpoints qualité de l'air
# Gère les routes liées à la qualité de l'air via OpenAQ
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.openaq import get_air_quality

router = APIRouter()

# ============================================================
# GET /api/air/{city}
# Retourne l'indice de qualité de l'air AQI + PM2.5 + NO2
# Exemple : GET /api/air/Paris
# ============================================================
@router.get("/air/{city}")
async def air_quality(city: str, db: Session = Depends(get_db)):
    try:
        data = await get_air_quality(city)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))