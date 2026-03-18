import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Détection de l'environnement Render
ON_RENDER = os.environ.get('RENDER', False)

if ON_RENDER:
    # Sur Render, on utilise PostgreSQL si DATABASE_URL est fournie, sinon SQLite
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        print("✅ Render: PostgreSQL configuré")
    else:
        # Fallback sur SQLite pour que l'API démarre quand même
        DATABASE_URL = "sqlite:///./citypulse.db"
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        print("⚠️ Render: DATABASE_URL non définie, utilisation de SQLite (mode dégradé)")
else:
    # En local, on utilise SQLite
    DATABASE_URL = "sqlite:///./citypulse.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    print("✅ Mode développement local: SQLite")

# Création des tables
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()