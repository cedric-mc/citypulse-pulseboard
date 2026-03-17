# ============================================================
# database.py — Connexion PostgreSQL (version compatible)
# CityPulse — Tableau de bord urbain intelligent
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from pathlib import Path

# Charge les variables du fichier .env
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dototenv(env_path)

# Récupère l'URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL non définie")

print(f"📦 DATABASE_URL = {DATABASE_URL}")

try:
    # Force l'encodage UTF-8 pour éviter les problèmes
    engine = create_engine(DATABASE_URL, connect_args={'client_encoding': 'utf8'})
    
    # Test de connexion
    with engine.connect() as conn:
        print("✅ Connexion à PostgreSQL réussie")
except Exception as e:
    print(f"❌ Erreur de connexion: {e}")
    print("⚠️ Mais ton endpoint /predict fonctionnera quand même sur Render !")
    # On continue malgré l'erreur pour que l'API démarre
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()