# ============================================================
# database.py — Connexion à la base de données PostgreSQL
# CityPulse — Tableau de bord urbain intelligent
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Charge les variables du fichier .env (clés API, DATABASE_URL)
load_dotenv()

# Récupère l'URL de connexion PostgreSQL depuis le .env
# Format : postgresql://user:password@host:port/database
DATABASE_URL = os.getenv("DATABASE_URL")

# Crée le moteur SQLAlchemy — c'est lui qui gère la connexion
# avec PostgreSQL via psycopg2
engine = create_engine(DATABASE_URL)

# Crée une "usine" à sessions — chaque requête HTTP aura
# sa propre session de BDD indépendante
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base dont hériteront tous nos modèles (tables)
# définis dans models.py
Base = declarative_base()

# ============================================================
# Dépendance FastAPI — injectée dans chaque endpoint
# Ouvre une session, l'utilise, puis la ferme proprement
# ============================================================
def get_db():
    db = SessionLocal()
    try:
        yield db        # Fournit la session à l'endpoint
    finally:
        db.close()      # Ferme toujours la session, même en cas d'erreur