import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path("back") / ".env")

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()
cur.execute("TRUNCATE TABLE events;")
conn.commit()
cur.close()
conn.close()
print("✅ Table events vidée !")