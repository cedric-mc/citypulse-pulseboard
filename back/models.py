# ============================================================
# models.py — Définition des tables PostgreSQL
# Chaque classe = une table dans la base de données
# SQLAlchemy traduit ces classes en SQL automatiquement
# ============================================================

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Time, Text
from sqlalchemy.sql import func
from database import Base


# ============================================================
# Table : weather_data
# Stocke les données météo récupérées via OpenWeatherMap
# ============================================================
class WeatherData(Base):
    __tablename__ = "weather_data"

    id          = Column(Integer, primary_key=True, index=True)
    city        = Column(String, index=True)            # Nom de la ville (ex: "Paris")
    temperature = Column(Float)                         # Température en °C
    feels_like  = Column(Float)                         # Température ressentie en °C
    humidity    = Column(Integer)                       # Humidité en %
    wind_speed  = Column(Float)                         # Vitesse du vent en m/s
    description = Column(String)                        # Description météo (ex: "ciel dégagé")
    icon        = Column(String)                        # Code icône OpenWeatherMap (ex: "01d")
    measured_at = Column(DateTime, default=func.now())  # Timestamp automatique


# ============================================================
# Table : air_quality_data
# Stocke les données qualité de l'air via OpenWeatherMap
# ============================================================
class AirQualityData(Base):
    __tablename__ = "air_quality"

    id          = Column(Integer, primary_key=True, index=True)
    city        = Column(String, index=True)            # Nom de la ville
    aqi         = Column(Integer)                       # Air Quality Index (1=Bon → 5=Très mauvais)
    pm25        = Column(Float)                         # Particules fines PM2.5 en µg/m³
    no2         = Column(Float)                         # Dioxyde d'azote NO2 en µg/m³
    o3          = Column(Float)                         # Ozone O3 en µg/m³
    measured_at = Column(DateTime, default=func.now())  # Timestamp automatique


# ============================================================
# Table : events
# Stocke les événements publics récupérés via OpenAgenda
# ============================================================
class Event(Base):
    __tablename__ = "events"

    id          = Column(Integer, primary_key=True, index=True)
    city        = Column(String, index=True)            # Nom de la ville
    external_id = Column(String, unique=True)           # ID provenant d'OpenAgenda
    title       = Column(String)                        # Titre de l'événement
    description = Column(Text)                         # Description longue
    event_date  = Column(Date)                          # Date de l'événement
    start_time  = Column(Time)                          # Heure de début
    location    = Column(String)                        # Lieu (nom du lieu)
    category    = Column(String)                        # Catégorie (Culture, Loisirs...)
    url         = Column(String, nullable=True)         # URL directe vers OpenAgenda
    # Coordonnées GPS réelles du lieu de l'event
    # Retournées par OpenAgenda via location.latitude / location.longitude
    # Utilisées par MapSection pour placer les marqueurs précisément
    # nullable=True car certains events n'ont pas de géolocalisation
    lat         = Column(Float, nullable=True)          # Latitude GPS du lieu
    lon         = Column(Float, nullable=True)          # Longitude GPS du lieu
    # Adresse complète du lieu — utilisée dans le popup carte
    # et pour le bouton itinéraire Google Maps
    address     = Column(String, nullable=True)         # Adresse complète du lieu
    created_at  = Column(DateTime, default=func.now())  # Timestamp automatique