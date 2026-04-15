"""
API Integration Layer
Handles all external API calls with caching and error handling
"""

import os
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

import requests
import streamlit as st


class APIError(Exception):
    pass


class CityNotFoundError(Exception):
    pass


@st.cache_data(ttl=600)  # Cache for 10 minutes
def fetch_city_coordinates(city: str, api_key: str) -> Tuple[float, float, str]:
    """Geocode city name to coordinates."""
    resp = requests.get(
        "http://api.openweathermap.org/geo/1.0/direct",
        params={"q": city, "limit": 1, "appid": api_key},
        timeout=8,
    )
    
    if resp.status_code != 200:
        raise APIError(f"Geocoding failed: HTTP {resp.status_code}")
    
    data = resp.json()
    if not data:
        raise CityNotFoundError(f"City '{city}' not found")
    
    entry = data[0]
    name = entry.get("name", city)
    country = entry.get("country", "")
    resolved = f"{name}, {country}" if country else name
    
    return entry["lat"], entry["lon"], resolved


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_current_pollution(lat: float, lon: float, api_key: str) -> Dict:
    """Fetch current air pollution data."""
    resp = requests.get(
        "http://api.openweathermap.org/data/2.5/air_pollution",
        params={"lat": lat, "lon": lon, "appid": api_key},
        timeout=8,
    )
    
    if resp.status_code != 200:
        raise APIError(f"Air Pollution API failed: HTTP {resp.status_code}")
    
    payload = resp.json()
    entry = payload["list"][0]
    components = entry["components"]
    
    return {
        "aqi_index": entry["main"]["aqi"],  # 1-5 scale
        "pm25": components.get("pm2_5", 0.0),
        "pm10": components.get("pm10", 0.0),
        "no2": components.get("no2", 0.0),
        "o3": components.get("o3", 0.0),
        "co": round(components.get("co", 0.0) / 1000, 4),  # Convert to mg/m³
        "so2": components.get("so2", 0.0),
        "nh3": components.get("nh3", 0.0),
        "timestamp": entry.get("dt", int(time.time()))
    }


@st.cache_data(ttl=300)
def fetch_current_weather(lat: float, lon: float, api_key: str) -> Dict:
    """Fetch current weather conditions."""
    resp = requests.get(
        "http://api.openweathermap.org/data/2.5/weather",
        params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"},
        timeout=8,
    )
    
    if resp.status_code != 200:
        raise APIError(f"Weather API failed: HTTP {resp.status_code}")
    
    d = resp.json()
    return {
        "temp_c": round(d["main"]["temp"], 1),
        "feels_like": round(d["main"]["feels_like"], 1),
        "temp_min": round(d["main"]["temp_min"], 1),
        "temp_max": round(d["main"]["temp_max"], 1),
        "humidity": d["main"]["humidity"],
        "pressure": d["main"]["pressure"],
        "wind_speed": round(d["wind"]["speed"] * 3.6, 1),  # m/s to km/h
        "wind_deg": d["wind"].get("deg", 0),
        "clouds": d["clouds"]["all"],
        "visibility": d.get("visibility", 10000),
        "description": d["weather"][0]["description"].capitalize(),
        "icon": d["weather"][0]["icon"],
        "sunrise": d["sys"]["sunrise"],
        "sunset": d["sys"]["sunset"],
        "timestamp": d["dt"]
    }


@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_historical_pollution(lat: float, lon: float, days: int, 
                               api_key: str) -> List[Dict]:
    """Fetch historical pollution data (up to 7 days on free tier)."""
    now = int(time.time())
    start = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    
    resp = requests.get(
        "http://api.openweathermap.org/data/2.5/air_pollution/history",
        params={"lat": lat, "lon": lon, "start": start, "end": now, "appid": api_key},
        timeout=15,
    )
    
    if resp.status_code != 200:
        raise APIError(f"History API failed: HTTP {resp.status_code}")
    
    records = resp.json().get("list", [])
    if not records:
        return []
    
    # Group by date and average
    buckets = defaultdict(list)
    for rec in records:
        date_str = datetime.fromtimestamp(rec["dt"], tz=timezone.utc).strftime("%Y-%m-%d")
        c = rec.get("components", {})
        buckets[date_str].append({
            "pm25": c.get("pm2_5", 0.0),
            "pm10": c.get("pm10", 0.0),
            "no2": c.get("no2", 0.0),
            "o3": c.get("o3", 0.0),
            "co": round(c.get("co", 0.0) / 1000, 4),
            "aqi": rec["main"]["aqi"]
        })
    
    daily = []
    for date_str in sorted(buckets):
        rows = buckets[date_str]
        daily.append({
            "date": date_str,
            "pm25": round(sum(r["pm25"] for r in rows) / len(rows), 2),
            "pm10": round(sum(r["pm10"] for r in rows) / len(rows), 2),
            "no2": round(sum(r["no2"] for r in rows) / len(rows), 2),
            "o3": round(sum(r["o3"] for r in rows) / len(rows), 2),
            "co": round(sum(r["co"] for r in rows) / len(rows), 4),
            "aqi_index": round(sum(r["aqi"] for r in rows) / len(rows), 1)
        })
    
    return daily[-days:]


def reverse_geocode(lat: float, lon: float, api_key: str) -> str:
    """Convert coordinates to city name."""
    resp = requests.get(
        "http://api.openweathermap.org/geo/1.0/reverse",
        params={"lat": lat, "lon": lon, "limit": 1, "appid": api_key},
        timeout=8,
    )
    
    if resp.status_code != 200 or not resp.json():
        return f"{lat:.4f}, {lon:.4f}"
    
    entry = resp.json()[0]
    name = entry.get("name", "")
    country = entry.get("country", "")
    return f"{name}, {country}" if country else name


def get_api_key() -> Optional[str]:
    """Get API key from secrets or environment."""
    try:
        return st.secrets.get("OPENWEATHER_API_KEY", "")
    except Exception:
        return os.environ.get("OPENWEATHER_API_KEY", "")


def owm_aqi_to_us_aqi(owm_index: int) -> float:
    """Convert OWM 1-5 index to approximate US AQI."""
    mapping = {1: 25, 2: 75, 3: 125, 4: 175, 5: 275}
    return float(mapping.get(owm_index, 0))
