# ============================================================
# models.py — Définition des tables PostgreSQL
# Chaque classe = une table dans la base de données
# SQLAlchemy traduit ces classes en SQL automatiquement
# ============================================================

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Time, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# ============================================================
# Table : weather_data
# Stocke les données météo récupérées via OpenWeatherMap
# ============================================================
class WeatherData(Base):
    __tablename__ = "weather_data"

    id          = Column(Integer, primary_key=True, index=True)
    city        = Column(String, index=True)
    temperature = Column(Float)
    feels_like  = Column(Float)
    humidity    = Column(Integer)
    wind_speed  = Column(Float)
    description = Column(String)
    icon_code   = Column(String)
    measured_at = Column(DateTime, default=func.now())


# ============================================================
# Table : air_quality_data
# Stocke les données qualité de l'air via OpenWeatherMap
# ============================================================
class AirQualityData(Base):
    __tablename__ = "air_quality"

    id         = Column(Integer, primary_key=True, index=True)
    city       = Column(String, index=True)
    aqi        = Column(Integer)
    pm25       = Column(Float)
    no2        = Column(Float)
    o3         = Column(Float)
    measured_at = Column(DateTime, default=func.now())


# ============================================================
# Table : events
# Stocke les événements publics récupérés via OpenAgenda
# ============================================================
class Event(Base):
    __tablename__ = "events"

    id          = Column(Integer, primary_key=True, index=True)
    city        = Column(String, index=True)
    external_id = Column(String, unique=True)
    title       = Column(String)
    description = Column(Text)
    event_date  = Column(Date)
    start_time  = Column(Time)
    location    = Column(String)
    category    = Column(String)
    created_at  = Column(DateTime, default=func.now())

# ============================================================
# Table : urban_scores
# Stocke le score urbain calculé pour chaque ville
# Score global = combinaison météo + qualité air + événements
# ============================================================
class UrbanScore(Base):
    __tablename__ = "urban_scores"

    id             = Column(Integer, primary_key=True, index=True)
    city           = Column(String, index=True)
    score          = Column(Float)
    weather_score  = Column(Float)
    air_score      = Column(Float)
    events_score   = Column(Float)
    created_at     = Column(DateTime, default=func.now())
