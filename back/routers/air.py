# ============================================================
# routers/air.py — Endpoints qualité de l'air
# Gère les routes liées à la qualité de l'air via OpenAQ
# ============================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.data_pipeline import refresh_city_data, get_latest_air_quality, air_to_response

router = APIRouter()

# ============================================================
# GET /api/air/{city}
# Retourne l'indice de qualité de l'air AQI + PM2.5 + NO2
# Exemple : GET /api/air/Paris
# ============================================================
@router.get("/air/{city}")
async def air_quality(city: str, db: Session = Depends(get_db)):
    try:
        await refresh_city_data(db, city)
        row = get_latest_air_quality(db, city)
        if not row:
            raise HTTPException(status_code=404, detail="Aucune donnée qualité de l'air en base")
        return air_to_response(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))