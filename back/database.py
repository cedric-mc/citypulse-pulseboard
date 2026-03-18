import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

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
    # En local, on utilise SQLite
    DATABASE_URL = "sqlite:///./citypulse.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    print("✅ Mode développement: SQLite")

# Création des tables
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()