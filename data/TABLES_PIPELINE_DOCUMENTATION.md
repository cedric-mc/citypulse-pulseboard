# CityPulse - Documentation des tables et pipelines

Ce document decrit la structure des tables PostgreSQL et le fonctionnement des pipelines de collecte.

## 1) Tables PostgreSQL

### Table weather_data
Role:
Stocke les mesures meteo horodatees par ville.

Colonnes:
- id: SERIAL, cle primaire.
- city: VARCHAR(255), ville (normalisee).
- temperature: DECIMAL(5,2), temperature en degres C.
- feels_like: DECIMAL(5,2), ressenti en degres C.
- humidity: INTEGER, humidite en pourcentage.
- wind_speed: DECIMAL(5,2), vitesse du vent.
- description: VARCHAR(255), description meteo.
- icon: VARCHAR(10), code icone OpenWeather (ex: 01d).
- measured_at: TIMESTAMP, horodatage de la mesure.

Contraintes:
- CHECK humidity entre 0 et 100.
- UNIQUE (city, measured_at).

Index:
- idx_weather_city_time (city, measured_at DESC).

### Table air_quality
Role:
Stocke les mesures de qualite de l'air horodatees par ville.

Colonnes:
- id: SERIAL, cle primaire.
- city: VARCHAR(255), ville (normalisee).
- aqi: INTEGER, indice de qualite de l'air.
- pm25: DECIMAL(6,2), particules PM2.5.
- no2: DECIMAL(6,2), dioxyde d'azote.
- o3: DECIMAL(6,2), ozone.
- measured_at: TIMESTAMP, horodatage de la mesure.

Contraintes:
- CHECK aqi entre 1 et 5.
- UNIQUE (city, measured_at).

Index:
- idx_air_quality_city_time (city, measured_at DESC).

### Table events
Role:
Stocke les evenements publics associes aux villes.

Colonnes:
- id: SERIAL, cle primaire.
- city: VARCHAR(255), ville (normalisee).
- external_id: VARCHAR(100), identifiant externe source.
- title: VARCHAR(255), titre de l'evenement.
- description: TEXT, description.
- event_date: DATE, date de l'evenement.
- start_time: TIME, heure de debut.
- location: VARCHAR(255), lieu.
- category: VARCHAR(100), categorie.
- created_at: TIMESTAMP, date d'insertion.

Contraintes:
- external_id UNIQUE.

Index:
- idx_events_city_date (city, event_date).

### Table users
Role:
Extension future (hors pipeline actuel).

Colonnes:
- id, username, email, password_hash, created_at.

## 2) Flux pipeline

Le pipeline principal est compose de trois etapes:

1. Collecte
- Meteo: OpenWeather Current Weather.
- Air: OpenWeather Air Pollution.
- Evenements: OpenAgenda.

2. Normalisation
- Normalisation des noms de ville (title case, fallback Paris).
- Conversions numeriques robustes (float/int).
- Clamp AQI dans [1, 5].
- Parsing ISO date/heure des evenements.
- Troncature defensive de certains champs texte.

3. Chargement en base
- Insertion d'une ligne weather_data par ville et par cycle.
- Insertion d'une ligne air_quality par ville et par cycle.
- Insertion conditionnelle des events (deduplication sur external_id).

Le score urbain est calcule en memoire a partir des donnees collectees, puis expose via l'API. Il n'est pas stocke dans une table dediee.

## 3) Scripts pipeline

### collect_public_data.py
Role:
Execute un cycle de collecte pour une liste de villes.

Comportement:
- Appels API asynchrones weather + air + events.
- Normalisation des payloads.
- Insertions SQLAlchemy avec commit en fin de cycle.

### hourly_ingest.py
Role:
Lance une boucle d'ingestion continue.

Comportement:
- Intervalle par defaut: 3600 secondes (1 heure).
- Option --once pour un cycle unique.

### simulate_48h.py
Role:
Injecte des donnees simulees pour tests/demo.

## 4) Execution

Prerequis:
- Variables d'environnement configurees (.env racine).
- Base PostgreSQL accessible via DATABASE_URL.

Depuis le dossier back:

Initialiser le schema:
python ../data/init.py

Collecte ponctuelle:
python -m pipelines.collect_public_data --cities Paris Lyon Marseille

Ingestion horaire continue:
python -m pipelines.hourly_ingest --cities Paris Lyon Marseille

Test rapide (1 cycle):
python -m pipelines.hourly_ingest --once

Simulation de donnees:
python -m pipelines.simulate_48h --hours 48 --cities Paris Lyon Marseille

## 5) API et ecriture BDD

Important:
Les endpoints API de lecture (weather, air, events, score) sont prevus pour lire la base et ne doivent pas declencher d'insertion de donnees.

Les insertions regulieres doivent etre declenchees par les scripts pipeline (collect_public_data.py ou hourly_ingest.py).
