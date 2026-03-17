# ============================================================
# main.py — Point d'entrée de l'application FastAPI
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import weather, air, events, score, predict  # ← predict ajouté

# Création des tables PostgreSQL
Base.metadata.create_all(bind=engine)

# Initialisation de l'application
app = FastAPI(
    title="CityPulse API",
    description="Tableau de bord urbain intelligent",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
app.include_router(weather.router, prefix="/api", tags=["🌤️ Météo"])
app.include_router(air.router,     prefix="/api", tags=["🌬️ Qualité de l'air"])
app.include_router(events.router,  prefix="/api", tags=["🎭 Événements"])
app.include_router(score.router,   prefix="/api", tags=["📊 Score urbain"])
app.include_router(predict.router, prefix="/api", tags=["🤖 Prédictions IA"])  # ← TON endpoint

# Route racine
@app.get("/")
def root():
    return {
        "message": "CityPulse API",
        "status": "running",
        "docs": "/docs"
    }