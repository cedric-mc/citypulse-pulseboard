import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

# Charge les variables du fichier .env (clés API, DATABASE_URL)
LOCAL_ENV_PATH = Path(__file__).resolve().parent / ".env"
ROOT_ENV_PATH = ROOT_DIR / "back" / ".env"
load_dotenv(ROOT_ENV_PATH)
load_dotenv(LOCAL_ENV_PATH)

def init_db():
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL introuvable. Vérifiez le fichier .env à la racine du projet.")

        # Connexion à la base de données PostgreSQL avec l'URL de connexion depuis les variables d'environnement
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Lecture du fichier SQL
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            cur.execute(f.read())
        
        conn.commit()
        print("✅ Base de données initialisée avec succès !")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    init_db()
