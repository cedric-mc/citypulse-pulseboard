-- ============================================================
-- CityPulse - Schema PostgreSQL normalise
-- ============================================================

-- Nettoyage (ordre inverse des dependances)
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS air_quality;
DROP TABLE IF EXISTS weather_data;
DROP TABLE IF EXISTS users;

-- 1) Table Météo
CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    temperature DECIMAL(5,2),
    feels_like DECIMAL(5,2),
    humidity INTEGER CHECK (humidity >= 0 AND humidity <= 100),
    wind_speed DECIMAL(5,2),
    description VARCHAR(255),
    icon VARCHAR(10),
    measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (city, measured_at)
);

-- 2) Qualite de l'air horaire
CREATE TABLE air_quality (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    aqi INTEGER NOT NULL CHECK (aqi BETWEEN 1 AND 5),
    pm25 DECIMAL(6,2),
    no2 DECIMAL(6,2),
    o3 DECIMAL(6,2),
    measured_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (city, measured_at)
);

-- 3) Evenements publics
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    external_id VARCHAR(100) UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    start_time TIME,
    location VARCHAR(255),                                     -- Nom du lieu
    category VARCHAR(100),
    url VARCHAR(500),                                          -- URL directe OpenAgenda
    lat DECIMAL(10,7),                                         -- Latitude GPS du lieu
    lon DECIMAL(10,7),                                         -- Longitude GPS du lieu
    address VARCHAR(500),                                      -- Adresse complète du lieu
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4) Utilisateurs (future extension)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index pour accélération dashboard et pipelines
CREATE INDEX idx_weather_city_time ON weather_data (city, measured_at DESC);
CREATE INDEX idx_air_quality_city_time ON air_quality (city, measured_at DESC);
CREATE INDEX idx_events_city_date ON events (city, event_date);