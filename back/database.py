<<<<<<< Updated upstream
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
=======
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base  # on importe Base depuis models

# Détection de l'environnement (Render ou local)
ON_RENDER = os.environ.get('RENDER', False)

if ON_RENDER:
    # En production sur Render, on utilise PostgreSQL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("❌ DATABASE_URL must be set on Render")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    print("✅ Mode production: PostgreSQL")
else:
    # En local, on utilise SQLite (pas de problèmes de connexion)
    DATABASE_URL = "sqlite:///./citypulse.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    print("✅ Mode développement: SQLite")

# Création des tables (pour SQLite comme pour PostgreSQL)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
>>>>>>> Stashed changes

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()