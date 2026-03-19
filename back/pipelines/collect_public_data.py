from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy.orm import Session

from database import SessionLocal
from models import WeatherData, AirQualityData, Event
from services.openweather import get_weather
from services.openaq import get_air_quality
from services.openagenda import get_events
from pipelines.normalization import (
    normalize_city,
    normalize_weather_payload,
    normalize_air_payload,
    normalize_event_payload,
)

DEFAULT_CITIES = ["Paris", "Lyon", "Marseille", "Lille", "Bordeaux"]


def calculate_weather_score(weather: dict) -> float:
    score = 100.0
    temp = weather.get("temperature", 20)
    if temp < 0 or temp > 35:
        score -= 40
    elif temp < 10 or temp > 30:
        score -= 20
    elif temp < 15 or temp > 25:
        score -= 10

    humidity = weather.get("humidity", 50)
    if humidity > 80:
        score -= 20
    elif humidity > 70:
        score -= 10

    wind = weather.get("wind_speed", 0)
    if wind > 50:
        score -= 30
    elif wind > 30:
        score -= 15
    elif wind > 20:
        score -= 5

    return max(0.0, min(100.0, score))


def calculate_air_score(air: dict) -> float:
    scores = {1: 100.0, 2: 75.0, 3: 50.0, 4: 25.0, 5: 10.0}
    return scores.get(air.get("aqi", 3), 50.0)


def calculate_events_score(events_count: int) -> float:
    if events_count >= 8:
        return 100.0
    if events_count >= 5:
        return 80.0
    if events_count >= 3:
        return 60.0
    if events_count >= 1:
        return 40.0
    return 20.0


def compute_global_score(weather: dict, air: dict, events_count: int) -> dict:
    weather_score = calculate_weather_score(weather)
    air_score     = calculate_air_score(air)
    events_score  = calculate_events_score(events_count)
    global_score  = round(weather_score * 0.4 + air_score * 0.4 + events_score * 0.2, 2)

    return {
        "score":         global_score,
        "weather_score": round(weather_score, 2),
        "air_score":     round(air_score, 2),
        "events_score":  round(events_score, 2),
    }


def insert_weather(db: Session, city_name: str, payload: dict) -> WeatherData:
    row = WeatherData(
        city        = city_name,
        temperature = payload["temperature"],
        feels_like  = payload["feels_like"],
        humidity    = payload["humidity"],
        wind_speed  = payload["wind_speed"],
        description = payload["description"],
        icon        = payload["icon"],
        measured_at = datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(row)
    return row


def insert_air(db: Session, city_name: str, payload: dict) -> AirQualityData:
    row = AirQualityData(
        city        = city_name,
        aqi         = payload["aqi"],
        pm25        = payload["pm25"],
        no2         = payload["no2"],
        o3          = payload["o3"],
        measured_at = datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(row)
    return row


def upsert_events(db: Session, city_name: str, events: list[dict]) -> int:
    inserted = 0
    for event in events:
        payload = normalize_event_payload(city_name, event)
        if not payload:
            continue

        ext = payload.get("external_id")
        if ext:
            exists = db.query(Event).filter(Event.external_id == ext).first()
            if exists:
                # Met à jour l'URL si elle était manquante sur un event déjà en BDD
                if not exists.url and payload.get("url"):
                    exists.url = payload.get("url")
                continue

        row = Event(
            city        = city_name,
            external_id = payload["external_id"],
            title       = payload["title"],
            description = payload["description"],
            event_date  = payload["event_date"],
            start_time  = payload["start_time"],
            location    = payload["location"],
            category    = payload["category"],
            url         = payload.get("url"),
        )
        db.add(row)
        inserted += 1
    return inserted


async def collect_for_city(db: Session, city_name: str) -> dict:
    normalized_city = normalize_city(city_name)

    weather_raw, air_raw, events_raw = await asyncio.gather(
        get_weather(normalized_city),
        get_air_quality(normalized_city),
        get_events(normalized_city),
    )

    events = events_raw.get("events", []) if isinstance(events_raw, dict) else []

    # DEBUG — affiche le premier event brut retourné par OpenAgenda
    # Permet de vérifier si le champ "url" est bien présent
    if events:
        print("=== DEBUG EVENT BRUT ===")
        print(events[0])
        print("========================")

    weather = normalize_weather_payload(normalized_city, weather_raw)
    air     = normalize_air_payload(normalized_city, air_raw)
    score   = compute_global_score(weather, air, len(events))

    insert_weather(db, normalized_city, weather)
    insert_air(db, normalized_city, air)
    inserted_events = upsert_events(db, normalized_city, events)

    return {
        "city":            normalized_city,
        "events_inserted": inserted_events,
        "events_seen":     len(events),
        "score":           score,
    }


async def run(cities: Iterable[str]) -> list[dict]:
    db = SessionLocal()
    try:
        results = []
        for city in cities:
            result = await collect_for_city(db, city)
            results.append(result)
        db.commit()
        return results
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collecte des donnees API publiques CityPulse")
    parser.add_argument(
        "--cities",
        nargs="*",
        default=DEFAULT_CITIES,
        help="Liste des villes a collecter (defaut: Paris Lyon Marseille Lille Bordeaux)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = asyncio.run(run(args.cities))
    for item in results:
        print(
            f"[OK] {item['city']} - events vus={item['events_seen']} inseres={item['events_inserted']}"
        )


if __name__ == "__main__":
    main()