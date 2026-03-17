# ============================================================
# main.py — Point d'entrée de l'application FastAPI
# C'est ici que tout démarre — serveur, routes, middleware
# Lancer avec : uvicorn main:app --reload
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import weather, air, events, score, predict  # 👈 AJOUT DE predict

# ============================================================
# Création des tables PostgreSQL automatiquement
# SQLAlchemy lit les modèles de models.py et crée les tables
# si elles n'existent pas encore dans la BDD
# ============================================================
Base.metadata.create_all(bind=engine)

# ============================================================
# Initialisation de l'application FastAPI
# title/description/version → visibles dans le Swagger /docs
# ============================================================
app = FastAPI(
    title="CityPulse API",
    description="Tableau de bord urbain intelligent — Paris 🏙️",
    version="1.0.0"
)

# ============================================================
# Middleware CORS — Cross Origin Resource Sharing
# Permet au front React (autre port/domaine) d'appeler l'API
# Sans ça, le navigateur bloquerait les requêtes du front
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Autorise tous les domaines (à restreindre en production)
    allow_methods=["*"],      # Autorise GET, POST, PUT, DELETE etc.
    allow_headers=["*"],      # Autorise tous les headers HTTP
)

# ============================================================
# Inclusion des routers — chaque fichier gère une fonctionnalité
# prefix="/api" → tous les endpoints commencent par /api/...
# tags → catégories visibles dans le Swagger /docs
# ============================================================
app.include_router(weather.router, prefix="/api", tags=["🌤️ Météo"])
app.include_router(air.router,     prefix="/api", tags=["🌬️ Qualité de l'air"])
app.include_router(events.router,  prefix="/api", tags=["🎭 Événements"])
app.include_router(score.router,   prefix="/api", tags=["📊 Score urbain"])
app.include_router(predict.router, prefix="/api", tags=["🤖 Prédictions IA"])  # 👈 AJOUT DE LA LIGNE

# ============================================================
# Route racine — endpoint de santé de l'API
# Accessible sur http://127.0.0.1:8000/
# Utile pour vérifier que le serveur tourne
# ============================================================
@app.get("/")
def root():
    return {
        "message": "CityPulse API — Paris 🏙️",
        "status": "running",
        "docs": "http://127.0.0.1:8000/docs",
        "version": "1.0.0"
    }