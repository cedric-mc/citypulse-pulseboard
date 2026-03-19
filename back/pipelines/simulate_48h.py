from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta

from database import SessionLocal
from models import WeatherData, AirQualityData, Event

DEFAULT_CITIES = ["Paris", "Lyon", "Marseille"]


def simulate_for_city(db, city_name: str, start: datetime, hours: int) -> None:
    for i in range(hours):
        ts = start + timedelta(hours=i)

        temperature = round(random.uniform(7.0, 29.0), 2)
        feels_like  = round(temperature + random.uniform(-2.0, 2.0), 2)
        humidity    = random.randint(30, 85)
        wind_speed  = round(random.uniform(3.0, 35.0), 2)

        aqi  = random.randint(1, 5)
        pm25 = round(random.uniform(4.0, 40.0), 2)
        no2  = round(random.uniform(8.0, 90.0), 2)
        o3   = round(random.uniform(15.0, 110.0), 2)

        db.add(
            WeatherData(
                city        = city_name,
                temperature = temperature,
                feels_like  = feels_like,
                humidity    = humidity,
                wind_speed  = wind_speed,
                description = "simulation",
                icon        = "02d",
                measured_at = ts,
            )
        )

        db.add(
            AirQualityData(
                city        = city_name,
                aqi         = aqi,
                pm25        = pm25,
                no2         = no2,
                o3          = o3,
                measured_at = ts,
            )
        )

        # Insère un event simulé toutes les 6h
        # url=None car ces events sont fictifs et n'ont pas de page OpenAgenda
        # Ils ne seront donc pas cliquables dans le dashboard — comportement attendu
        if i % 6 == 0:
            db.add(
                Event(
                    city        = city_name,
                    external_id = f"sim-{city_name.lower()}-{ts.strftime('%Y%m%d%H')}",
                    title       = f"Evenement simule {city_name}",
                    description = "Evenement genere pour validation pipeline.",
                    event_date  = ts.date(),
                    start_time  = ts.time().replace(microsecond=0),
                    location    = f"Centre {city_name}",
                    category    = "Simulation",
                    url         = None,  # ← pas d'URL pour les events simulés
                )
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genere 48h de donnees de test")
    parser.add_argument("--hours",   type=int,  default=48)
    parser.add_argument("--cities",  nargs="*", default=DEFAULT_CITIES)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db   = SessionLocal()

    try:
        start = datetime.utcnow() - timedelta(hours=args.hours - 1)
        for city_name in args.cities:
            simulate_for_city(db, city_name, start, args.hours)

        db.commit()
        print(f"[OK] Donnees simulees inserees: {args.hours}h x {len(args.cities)} villes")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()