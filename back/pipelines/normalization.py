from __future__ import annotations

# ============================================================
# pipelines/normalization.py — Normalisation des données brutes
# Transforme les réponses des APIs externes en données propres
# prêtes à être insérées en base de données
# ============================================================

from datetime import datetime, timezone, timedelta
from typing import Any

# Fuseau horaire Paris (UTC+1 en hiver, UTC+2 en été)
# On utilise la conversion automatique via astimezone
PARIS_TZ = timezone(timedelta(hours=1))


def normalize_city(raw_city: str) -> str:
    """Normalise le nom d'une ville — strip + title case."""
    city = (raw_city or "").strip()
    if not city:
        return "Paris"
    return city.title()


def to_float(value: Any, default: float = 0.0, digits: int = 2) -> float:
    """Convertit une valeur en float arrondi, avec valeur par défaut."""
    try:
        return round(float(value), digits)
    except (TypeError, ValueError):
        return default


def to_int(value: Any, default: int = 0) -> int:
    """Convertit une valeur en entier, avec valeur par défaut."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Borne une valeur entre un minimum et un maximum."""
    return max(minimum, min(maximum, value))


def parse_iso_datetime(value: str | None) -> datetime | None:
    """Parse une date ISO 8601 en objet datetime, retourne None si invalide."""
    if not value:
        return None
    clean = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(clean)
    except ValueError:
        return None


# ============================================================
# Normalisation météo
# Transforme la réponse OpenWeatherMap en payload BDD propre
# ============================================================
def normalize_weather_payload(city: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "city":        normalize_city(city),
        "temperature": to_float(payload.get("temperature")),
        "feels_like":  to_float(payload.get("feels_like")),
        "humidity":    to_int(payload.get("humidity")),
        "wind_speed":  to_float(payload.get("wind_speed")),
        "description": str(payload.get("description") or "n/a")[:255],
        "icon":        str(payload.get("icon") or "")[:10],
    }


# ============================================================
# Normalisation qualité de l'air
# Transforme la réponse OpenAQ en payload BDD propre
# AQI borné entre 1 et 5 pour rester cohérent avec le modèle
# ============================================================
def normalize_air_payload(city: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "city": normalize_city(city),
        "aqi":  int(clamp(to_int(payload.get("aqi"), default=3), 1, 5)),
        "pm25": to_float(payload.get("pm25")),
        "no2":  to_float(payload.get("no2")),
        "o3":   to_float(payload.get("o3")),
    }


# ============================================================
# Normalisation événement
# Transforme la réponse OpenAgenda en payload BDD propre
# Retourne None si la date est absente (event invalide)
# Convertit les dates en heure de Paris pour cohérence
# ============================================================
def normalize_event_payload(city: str, event: dict[str, Any]) -> dict[str, Any] | None:
    date_raw = event.get("date")
    dt = parse_iso_datetime(date_raw)

    # Un event sans date est invalide → on le rejette
    if not dt:
        return None

    # Convertit en heure de Paris pour éviter les décalages UTC
    # OpenAgenda retourne des dates avec fuseau (+01:00 ou +02:00)
    # On normalise tout en heure Paris pour cohérence BDD/frontend
    try:
        dt_paris = dt.astimezone(PARIS_TZ)
    except Exception:
        dt_paris = dt

    event_date = dt_paris.date()
    start_time = dt_paris.time().replace(tzinfo=None)

    # URL directe vers la page de l'événement sur OpenAgenda
    # Champ séparé de external_id pour éviter toute confusion
    url = str(event.get("url") or "")[:500] or None

    return {
        "city":        normalize_city(city),
        # external_id — identifiant unique OpenAgenda de l'événement
        # Utilise "external_id" en priorité puis "id" comme fallback
        # Ne jamais utiliser l'URL comme identifiant (champ séparé)
        "external_id": str(event.get("external_id") or event.get("id") or "")[:100] or None,
        "title":       str(event.get("title") or "Sans titre")[:255],
        "description": str(event.get("description") or "") if event.get("description") else None,
        "event_date":  event_date,
        "start_time":  start_time,
        "location":    str(event.get("location") or "")[:255] or None,
        "category":    str(event.get("category") or "Evenement")[:100],
        # URL directe OpenAgenda — transmise au pipeline pour être
        # sauvegardée en BDD et retournée au frontend pour le lien cliquable
        "url":         url,
    }