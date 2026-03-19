from __future__ import annotations

from datetime import date, datetime
from sqlalchemy import func, or_, and_
from sqlalchemy.orm import Session

from models import AirQualityData, Event, WeatherData
from pipelines.collect_public_data import collect_for_city, compute_global_score
from pipelines.normalization import normalize_city


AQI_STATUS = {
    1: {"status": "Bon",          "color_code": "#00E400"},
    2: {"status": "Correct",      "color_code": "#FFFF00"},
    3: {"status": "Modere",       "color_code": "#FF7E00"},
    4: {"status": "Mauvais",      "color_code": "#FF0000"},
    5: {"status": "Tres mauvais", "color_code": "#8F3F97"},
}


async def refresh_city_data(db: Session, city: str) -> dict:
    try:
        result = await collect_for_city(db, city)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


def get_latest_weather(db: Session, city: str) -> WeatherData | None:
    city_name = normalize_city(city)
    return (
        db.query(WeatherData)
        .filter(func.lower(WeatherData.city) == city_name.lower())
        .order_by(WeatherData.measured_at.desc(), WeatherData.id.desc())
        .first()
    )


def get_latest_air_quality(db: Session, city: str) -> AirQualityData | None:
    city_name = normalize_city(city)
    return (
        db.query(AirQualityData)
        .filter(func.lower(AirQualityData.city) == city_name.lower())
        .order_by(AirQualityData.measured_at.desc(), AirQualityData.id.desc())
        .first()
    )


def get_events_for_city(db: Session, city: str, limit: int = 50) -> list[Event]:
    city_name = normalize_city(city)
    now      = datetime.now()
    today    = now.date()
    now_time = now.time()

    # Récupère les events à venir en filtrant par date ET heure France
    # — events futurs (date > aujourd'hui)
    # — events aujourd'hui dont l'heure n'est pas encore passée
    rows = (
        db.query(Event)
        .filter(
            func.lower(Event.city) == city_name.lower(),
            or_(
                Event.event_date > today,
                and_(
                    Event.event_date == today,
                    Event.start_time >= now_time
                )
            )
        )
        .order_by(Event.event_date.asc(), Event.start_time.asc())
        .limit(limit)
        .all()
    )

    if rows:
        # Dédoublonnage par titre — évite qu'un même événement
        # apparaisse deux fois s'il vient de deux agendas différents
        seen = set()
        unique_rows = []
        for row in rows:
            key = row.title.lower().strip()
            if key not in seen:
                seen.add(key)
                unique_rows.append(row)
        # Limite à 5 events max
        return unique_rows[:5]

    # Fallback — retourne les 5 prochains events futurs
    # filtrés par heure pour éviter les events passés
    fallback = (
        db.query(Event)
        .filter(
            func.lower(Event.city) == city_name.lower(),
            or_(
                Event.event_date > today,
                and_(
                    Event.event_date == today,
                    Event.start_time >= now_time
                )
            )
        )
        .order_by(Event.event_date.asc(), Event.start_time.asc())
        .limit(5)
        .all()
    )
    return fallback


def weather_to_response(row: WeatherData) -> dict:
    return {
        "city":        row.city,
        "temperature": row.temperature,
        "feels_like":  row.feels_like,
        "unit":        "Celsius",
        "humidity":    row.humidity,
        "wind_speed":  row.wind_speed,
        "description": row.description,
        "icon":        row.icon,
        "measured_at": row.measured_at.isoformat() if row.measured_at else None,
        "source":      "database",
    }


def air_to_response(row: AirQualityData) -> dict:
    status = AQI_STATUS.get(row.aqi, AQI_STATUS[3])
    return {
        "city":        row.city,
        "aqi":         row.aqi,
        "status":      status["status"],
        "color_code":  status["color_code"],
        "pollutants": {
            "pm25": row.pm25,
            "no2":  row.no2,
            "o3":   row.o3,
        },
        "measured_at": row.measured_at.isoformat() if row.measured_at else None,
        "source":      "database",
    }


def events_to_response(rows: list[Event]) -> list[dict]:
    payload: list[dict] = []
    for row in rows:
        payload.append({
            "id":          row.id,
            "title":       row.title,
            "date":        row.event_date.isoformat() if row.event_date else None,
            "time":        row.start_time.isoformat() if row.start_time else None,
            "location":    row.location,
            "category":    row.category,
            "description": row.description,
            "url":         row.url,          # URL directe OpenAgenda
            # Coordonnées GPS réelles du lieu — utilisées par MapSection
            # pour placer les marqueurs précisément sur la carte
            "lat":         row.lat,          # Latitude GPS du lieu
            "lon":         row.lon,          # Longitude GPS du lieu
            # Adresse complète — utilisée dans le popup carte
            # et pour le bouton itinéraire Google Maps
            "address":     row.address,      # Adresse complète du lieu
            "source":      "database",
        })
    return payload


def score_to_response(city: str, weather: WeatherData, air: AirQualityData, events: list[Event]) -> dict:
    score = compute_global_score(
        {
            "temperature": weather.temperature,
            "humidity":    weather.humidity,
            "wind_speed":  weather.wind_speed,
        },
        {"aqi": air.aqi},
        len(events),
    )

    return {
        "city":    normalize_city(city),
        "score":   score["score"],
        "details": {
            "weather_score": score["weather_score"],
            "air_score":     score["air_score"],
            "events_score":  score["events_score"],
        },
        "source": "computed_from_database",
    }