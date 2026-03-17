# ============================================================
# database.py — Connexion SQLite (version simplifiée pour le MVP)
# CityPulse — Tableau de bord urbain intelligent
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# On force SQLite (pas de .env, pas de PostgreSQL)
SQLALCHEMY_DATABASE_URL = "sqlite:///./citypulse.db"

# Crée le moteur SQLAlchemy avec SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Nécessaire pour SQLite
)

# Crée une "usine" à sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour les modèles
Base = declarative_base()

# ============================================================
# Dépendance FastAPI
# ============================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()