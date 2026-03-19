# CityPulse API - Contrat d'API

Base URL (prod):
- https://citypulse-pulseboard.onrender.com

Prefixe commun:
- /api

Format:
- Toutes les reponses sont en JSON.
- Les routes sont en GET uniquement pour la lecture.

## 1) Healthcheck

Endpoint:
- GET /

Reponse 200:
```json
{
  "message": "CityPulse API — Paris 🏙️",
  "status": "running",
  "docs": "http://127.0.0.1:8000/docs",
  "version": "1.0.0"
}
```

## 2) Meteo actuelle

Endpoint:
- GET /api/weather/{city}

Exemple:
- GET /api/weather/paris

Reponse 200:
```json
{
  "city": "Paris",
  "temperature": 22.5,
  "feels_like": 21.0,
  "unit": "Celsius",
  "humidity": 45,
  "wind_speed": 8.3,
  "description": "Partiellement nuageux",
  "icon": "03d",
  "measured_at": "2026-03-19T09:00:00",
  "source": "database"
}
```

## 3) Previsions meteo 24h

Endpoint:
- GET /api/forecast/{city}

Exemple:
- GET /api/forecast/paris

Reponse 200:
```json
{
  "city": "Paris",
  "forecasts": [
    {
      "time": "2026-03-19 12:00:00",
      "temperature": 19.0,
      "feels_like": 18.2,
      "humidity": 48,
      "description": "ciel degage",
      "icon": "01d",
      "icon_url": "https://openweathermap.org/img/wn/01d@2x.png"
    },
    {
      "time": "2026-03-19 15:00:00",
      "temperature": 20.1,
      "feels_like": 19.5,
      "humidity": 43,
      "description": "peu nuageux",
      "icon": "02d",
      "icon_url": "https://openweathermap.org/img/wn/02d@2x.png"
    }
  ]
}
```

## 4) Qualite de l'air

Endpoint:
- GET /api/air/{city}

Exemple:
- GET /api/air/paris

Reponse 200:
```json
{
  "city": "Paris",
  "aqi": 2,
  "status": "Correct",
  "color_code": "#FFFF00",
  "pollutants": {
    "pm25": 9.8,
    "no2": 14.2,
    "o3": 35.1
  },
  "measured_at": "2026-03-19T09:00:00",
  "source": "database"
}
```

## 5) Evenements

Endpoint:
- GET /api/events/{city}

Exemple:
- GET /api/events/paris

Reponse 200:
```json
[
  {
    "id": 101,
    "title": "Festival de la Soie",
    "date": "2026-03-20",
    "time": "10:00:00",
    "location": "Palais de la Bourse",
    "category": "Culture",
    "description": "Decouverte des metiers du tissage lyonnais.",
    "source": "database"
  }
]
```

Note:
- La route renvoie au maximum 5 evenements.
- Priorite aux evenements a venir; fallback sur les plus recents si aucun evenement futur.

## 6) Score urbain

Endpoint:
- GET /api/score/{city}

Exemple:
- GET /api/score/paris

Reponse 200:
```json
{
  "city": "Paris",
  "score": 74.4,
  "details": {
    "weather_score": 82.0,
    "air_score": 75.0,
    "events_score": 60.0
  },
  "source": "computed_from_database"
}
```

## 7) Erreurs

Exemple format erreur:
```json
{
  "detail": "Message d'erreur"
}
```

Codes courants:
- 404: donnees absentes (ex: aucune mesure meteo/air en base pour la ville demandee).
- 500: erreur interne (base indisponible, erreur service, exception non geree).
