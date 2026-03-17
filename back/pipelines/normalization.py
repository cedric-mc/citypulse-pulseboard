from __future__ import annotations

from datetime import datetime
from typing import Any


def normalize_city(raw_city: str) -> str:
    city = (raw_city or "").strip()
    if not city:
        return "Paris"
    return city.title()


def to_float(value: Any, default: float = 0.0, digits: int = 2) -> float:
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    clean = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(clean)
    except ValueError:
        return None


def normalize_weather_payload(city: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "city": normalize_city(city),
        "temperature": to_float(payload.get("temperature")),
        "feels_like": to_float(payload.get("feels_like")),
        "humidity": to_int(payload.get("humidity")),
        "wind_speed": to_float(payload.get("wind_speed")),
        "description": str(payload.get("description") or "n/a")[:255],
        "icon_code": str(payload.get("icon_code") or payload.get("icon") or "")[:10],
    }


def normalize_air_payload(city: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "city": normalize_city(city),
        "aqi": int(clamp(to_int(payload.get("aqi"), default=3), 1, 5)),
        "pm25": to_float(payload.get("pm25")),
        "no2": to_float(payload.get("no2")),
        "o3": to_float(payload.get("o3")),
    }


def normalize_event_payload(city: str, event: dict[str, Any]) -> dict[str, Any] | None:
    date_raw = event.get("date")
    dt = parse_iso_datetime(date_raw)
    event_date = dt.date() if dt else None
    start_time = dt.time().replace(tzinfo=None) if dt else None
    if not event_date:
        return None

    return {
        "city": normalize_city(city),
        "external_id": str(event.get("external_id") or event.get("id") or event.get("url") or "")[:100] or None,
        "title": str(event.get("title") or "Sans titre")[:255],
        "description": str(event.get("description") or "") if event.get("description") else None,
        "event_date": event_date,
        "start_time": start_time,
        "location": str(event.get("location") or "")[:255] or None,
        "category": str(event.get("category") or "Evenement")[:100],
    }
