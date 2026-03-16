# ============================================================
# models.py — Définition des tables PostgreSQL
# Chaque classe = une table dans la base de données
# SQLAlchemy traduit ces classes en SQL automatiquement
# ============================================================

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base

# ============================================================
# Table : weather_data
# Stocke les données météo récupérées via OpenWeatherMap
# ============================================================
class WeatherData(Base):
    __tablename__ = "weather_data"

    id          = Column(Integer, primary_key=True, index=True)  # Clé primaire auto-incrémentée
    city        = Column(String, index=True)   # Nom de la ville (ex: "Paris")
    temperature = Column(Float)                # Température en °C
    feels_like  = Column(Float)                # Température ressentie en °C
    humidity    = Column(Integer)              # Humidité en %
    wind_speed  = Column(Float)                # Vitesse du vent en m/s
    description = Column(String)              # Description météo (ex: "ciel dégagé")
    icon        = Column(String)              # Code icône OpenWeatherMap (ex: "01d")
    created_at  = Column(DateTime, default=func.now())  # Timestamp automatique

# ============================================================
# Table : air_quality_data
# Stocke les données qualité de l'air via OpenAQ / OpenWeatherMap
# ============================================================
class AirQualityData(Base):
    __tablename__ = "air_quality_data"

    id         = Column(Integer, primary_key=True, index=True)
    city       = Column(String, index=True)  # Nom de la ville
    aqi        = Column(Integer)             # Air Quality Index (1=Bon → 5=Très mauvais)
    pm25       = Column(Float)               # Particules fines PM2.5 en µg/m³
    no2        = Column(Float)               # Dioxyde d'azote NO2 en µg/m³
    created_at = Column(DateTime, default=func.now())  # Timestamp automatique

# ============================================================
# Table : urban_scores
# Stocke le score urbain calculé pour chaque ville
# Score global = combinaison météo + qualité air + événements
# ============================================================
class UrbanScore(Base):
    __tablename__ = "urban_scores"

    id             = Column(Integer, primary_key=True, index=True)
    city           = Column(String, index=True)  # Nom de la ville
    score          = Column(Float)               # Score global 0-100
    weather_score  = Column(Float)               # Sous-score météo (40% du total)
    air_score      = Column(Float)               # Sous-score qualité air (40% du total)
    events_score   = Column(Float)               # Sous-score événements (20% du total)
    created_at     = Column(DateTime, default=func.now())  # Timestamp automatique