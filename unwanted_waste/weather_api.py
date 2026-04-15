"""
weather_api.py
--------------
Fetches real-time pollutant data from OpenWeatherMap Air Pollution API.

Requires a free API key from https://openweathermap.org/api/air-pollution
Set it via:  export OPENWEATHER_API_KEY="your_key"
or pass it directly to fetch_pollution_by_city().
"""

from __future__ import annotations

import os
import requests

GEO_URL      = "http://api.openweathermap.org/geo/1.0/direct"
POLLUTION_URL = "http://api.openweathermap.org/data/2.5/air_pollution"


class APIKeyMissingError(Exception):
    pass


class CityNotFoundError(Exception):
    pass


class APIError(Exception):
    pass


def _get_coordinates(city: str, api_key: str) -> tuple[float, float, str]:
    """
    Resolve city name → (lat, lon, resolved_name).
    Raises CityNotFoundError if the city cannot be geocoded.
    """
    resp = requests.get(
        GEO_URL,
        params={"q": city, "limit": 1, "appid": api_key},
        timeout=8,
    )
    if resp.status_code != 200:
        raise APIError(f"Geocoding failed (HTTP {resp.status_code}): {resp.text}")

    data = resp.json()
    if not data:
        raise CityNotFoundError(f"City '{city}' not found. Check the spelling and try again.")

    entry = data[0]
    resolved = entry.get("name", city)
    country  = entry.get("country", "")
    if country:
        resolved = f"{resolved}, {country}"
    return entry["lat"], entry["lon"], resolved


def _fetch_pollution(lat: float, lon: float, api_key: str) -> dict:
    """
    Call the Air Pollution endpoint and return raw component values.
    """
    resp = requests.get(
        POLLUTION_URL,
        params={"lat": lat, "lon": lon, "appid": api_key},
        timeout=8,
    )
    if resp.status_code != 200:
        raise APIError(f"Air Pollution API failed (HTTP {resp.status_code}): {resp.text}")

    payload = resp.json()
    try:
        components = payload["list"][0]["components"]
    except (KeyError, IndexError) as exc:
        raise APIError(f"Unexpected API response format: {exc}") from exc

    return components


def fetch_pollution_by_city(city: str, api_key: str | None = None) -> dict:
    """
    Fetch real-time pollutant concentrations for a city.

    Parameters
    ----------
    city    : str  – city name (e.g. "Delhi", "London,GB")
    api_key : str  – OpenWeatherMap API key; falls back to OPENWEATHER_API_KEY env var

    Returns
    -------
    dict:
        {
            "city":  str,    # resolved city + country
            "pm25":  float,  # µg/m³
            "pm10":  float,  # µg/m³
            "no2":   float,  # µg/m³
            "co":    float,  # mg/m³  (API returns µg/m³, converted here)
            "o3":    float,  # µg/m³
            "so2":   float,  # µg/m³
            "nh3":   float,  # µg/m³
        }

    Raises
    ------
    APIKeyMissingError  – no key provided or found in env
    CityNotFoundError   – city geocoding returned no results
    APIError            – any HTTP or parsing error
    """
    key = api_key or os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not key:
        raise APIKeyMissingError(
            "No OpenWeatherMap API key found. "
            "Set the OPENWEATHER_API_KEY environment variable or enter it in the sidebar."
        )

    lat, lon, resolved_city = _get_coordinates(city, key)
    components = _fetch_pollution(lat, lon, key)

    return {
        "city": resolved_city,
        "pm25": components.get("pm2_5", 0.0),
        "pm10": components.get("pm10",  0.0),
        "no2":  components.get("no2",   0.0),
        # API gives CO in µg/m³ → convert to mg/m³ for our model
        "co":   round(components.get("co", 0.0) / 1000, 4),
        "o3":   components.get("o3",   0.0),
        "so2":  components.get("so2",  0.0),
        "nh3":  components.get("nh3",  0.0),
    }


def fetch_historical_pollution(city: str, days: int = 7, api_key: str | None = None) -> list[dict]:
    """
    Fetch hourly pollution history for the past `days` days and return
    one aggregated (mean) record per day.

    Parameters
    ----------
    city    : str
    days    : int  – number of past days (max 7 on free tier)
    api_key : str  – falls back to OPENWEATHER_API_KEY env var

    Returns
    -------
    list of dicts, one per day, each with:
        { "date": str (YYYY-MM-DD), "pm25": float, "pm10": float,
          "no2": float, "co": float, "o3": float }
    Sorted oldest → newest.
    """
    import time
    from datetime import datetime, timedelta, timezone

    key = api_key or os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not key:
        raise APIKeyMissingError("No API key provided.")

    lat, lon, _ = _get_coordinates(city, key)

    now   = int(time.time())
    start = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())

    resp = requests.get(
        "http://api.openweathermap.org/data/2.5/air_pollution/history",
        params={"lat": lat, "lon": lon, "start": start, "end": now, "appid": key},
        timeout=10,
    )
    if resp.status_code != 200:
        raise APIError(f"History API failed (HTTP {resp.status_code}): {resp.text}")

    records = resp.json().get("list", [])
    if not records:
        raise APIError("No historical data returned.")

    # Group by date and average
    from collections import defaultdict
    buckets: dict[str, list] = defaultdict(list)
    for rec in records:
        date_str = datetime.fromtimestamp(rec["dt"], tz=timezone.utc).strftime("%Y-%m-%d")
        c = rec.get("components", {})
        buckets[date_str].append({
            "pm25": c.get("pm2_5", 0.0),
            "pm10": c.get("pm10",  0.0),
            "no2":  c.get("no2",   0.0),
            "co":   round(c.get("co", 0.0) / 1000, 4),
            "o3":   c.get("o3",   0.0),
        })

    daily = []
    for date_str in sorted(buckets):
        rows = buckets[date_str]
        daily.append({
            "date": date_str,
            "pm25": round(sum(r["pm25"] for r in rows) / len(rows), 2),
            "pm10": round(sum(r["pm10"] for r in rows) / len(rows), 2),
            "no2":  round(sum(r["no2"]  for r in rows) / len(rows), 2),
            "co":   round(sum(r["co"]   for r in rows) / len(rows), 4),
            "o3":   round(sum(r["o3"]   for r in rows) / len(rows), 2),
        })

    return daily[-days:]  # keep only the last `days` entries


def reverse_geocode(lat: float, lon: float, api_key: str | None = None) -> str:
    """
    Convert (lat, lon) → human-readable city name using OWM reverse geocoding.

    Returns a string like "Delhi, IN", or "lat,lon" as fallback.
    """
    key = api_key or os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not key:
        return f"{lat:.4f},{lon:.4f}"

    resp = requests.get(
        "http://api.openweathermap.org/geo/1.0/reverse",
        params={"lat": lat, "lon": lon, "limit": 1, "appid": key},
        timeout=8,
    )
    if resp.status_code != 200 or not resp.json():
        return f"{lat:.4f},{lon:.4f}"

    entry = resp.json()[0]
    name    = entry.get("name", "")
    country = entry.get("country", "")
    return f"{name}, {country}" if country else name


def fetch_pollution_by_coords(lat: float, lon: float,
                               api_key: str | None = None) -> dict:
    """
    Fetch real-time pollutant concentrations for a (lat, lon) pair.
    Same return shape as fetch_pollution_by_city(), minus 'city'.
    """
    key = api_key or os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not key:
        raise APIKeyMissingError("No API key provided.")

    components = _fetch_pollution(lat, lon, key)
    city = reverse_geocode(lat, lon, key)

    return {
        "city": city,
        "pm25": components.get("pm2_5", 0.0),
        "pm10": components.get("pm10",  0.0),
        "no2":  components.get("no2",   0.0),
        "co":   round(components.get("co", 0.0) / 1000, 4),
        "o3":   components.get("o3",   0.0),
        "so2":  components.get("so2",  0.0),
        "nh3":  components.get("nh3",  0.0),
    }


def fetch_current_weather(lat: float, lon: float, api_key: str | None = None) -> dict:
    """
    Fetch current weather conditions for (lat, lon).

    Returns
    -------
    dict:
        {
            "temp_c":      float,   # temperature in Celsius
            "feels_like":  float,
            "humidity":    int,     # %
            "wind_kph":    float,
            "description": str,     # e.g. "overcast clouds"
            "icon":        str,     # OWM icon code e.g. "04d"
            "visibility":  int,     # metres
        }
    """
    key = api_key or os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not key:
        raise APIKeyMissingError("No API key provided.")

    resp = requests.get(
        "http://api.openweathermap.org/data/2.5/weather",
        params={"lat": lat, "lon": lon, "appid": key, "units": "metric"},
        timeout=8,
    )
    if resp.status_code != 200:
        raise APIError(f"Weather API failed (HTTP {resp.status_code}): {resp.text}")

    d = resp.json()
    return {
        "temp_c":      round(d["main"]["temp"], 1),
        "feels_like":  round(d["main"]["feels_like"], 1),
        "humidity":    d["main"]["humidity"],
        "wind_kph":    round(d["wind"]["speed"] * 3.6, 1),
        "description": d["weather"][0]["description"].capitalize(),
        "icon":        d["weather"][0]["icon"],
        "visibility":  d.get("visibility", 0),
    }


def fetch_official_aqi(lat: float, lon: float, api_key: str | None = None) -> dict:
    """
    Fetch OWM's official AQI index + raw components for (lat, lon).

    OWM AQI scale:
        1 = Good, 2 = Fair, 3 = Moderate, 4 = Poor, 5 = Very Poor

    Returns
    -------
    dict:
        {
            "owm_aqi":   int,    # 1–5
            "owm_label": str,
            "pm25":      float,
            "pm10":      float,
            "no2":       float,
            "o3":        float,
            "co":        float,  # mg/m³
        }
    """
    key = api_key or os.environ.get("OPENWEATHER_API_KEY", "").strip()
    if not key:
        raise APIKeyMissingError("No API key provided.")

    resp = requests.get(
        POLLUTION_URL,
        params={"lat": lat, "lon": lon, "appid": key},
        timeout=8,
    )
    if resp.status_code != 200:
        raise APIError(f"Air Pollution API failed (HTTP {resp.status_code}): {resp.text}")

    payload = resp.json()
    entry      = payload["list"][0]
    owm_index  = entry["main"]["aqi"]          # 1–5
    components = entry["components"]

    _OWM_LABELS = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}

    return {
        "owm_aqi":   owm_index,
        "owm_label": _OWM_LABELS.get(owm_index, "Unknown"),
        "pm25":      components.get("pm2_5", 0.0),
        "pm10":      components.get("pm10",  0.0),
        "no2":       components.get("no2",   0.0),
        "o3":        components.get("o3",    0.0),
        "co":        round(components.get("co", 0.0) / 1000, 4),
    }
