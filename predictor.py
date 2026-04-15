"""
predictor_updated.py
--------------------
Updated predictor for the new CSV-trained model.
Handles both simple pollutant input and full feature input.
"""

from __future__ import annotations
import pickle
import numpy as np
import pandas as pd
import streamlit as st

MODEL_PATH = "aqi_model.pkl"

# AQI scale (US EPA standard)
_AQI_SCALE = [
    (50,  "Good",
     "Air quality is satisfactory. Enjoy outdoor activities."),
    (100, "Moderate",
     "Acceptable air quality. Unusually sensitive people should consider limiting prolonged outdoor exertion."),
    (150, "Unhealthy for Sensitive Groups",
     "People with heart or lung disease, older adults, and children should reduce prolonged outdoor exertion."),
    (200, "Unhealthy",
     "Everyone may begin to experience health effects. Sensitive groups should avoid prolonged outdoor exertion."),
    (300, "Very Unhealthy",
     "Health alert: everyone may experience more serious health effects. Avoid prolonged outdoor exertion."),
    (float("inf"), "Hazardous",
     "Health warning of emergency conditions. Everyone should avoid all outdoor exertion."),
]


def _categorize(aqi: float) -> tuple[str, str]:
    """Return (category, health_advice) for a given AQI value."""
    for threshold, category, advice in _AQI_SCALE:
        if aqi <= threshold:
            return category, advice
    return _AQI_SCALE[-1][1], _AQI_SCALE[-1][2]


@st.cache_resource(show_spinner="Loading AQI model…")
def _get_bundle() -> dict:
    """Load model bundle with caching."""
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


def predict_aqi(data: dict) -> dict:
    """
    Predict AQI from pollutant readings.
    
    Parameters
    ----------
    data : dict
        Simplified format:
        {
            "pm25": float,   # PM2.5 (µg/m³)
            "pm10": float,   # PM10 (µg/m³)
            "no2":  float,   # NO2 (µg/m³)
            "so2":  float,   # SO2 (µg/m³) [optional]
            "co":   float,   # CO (mg/m³)
            "o3":   float,   # O3 (µg/m³) [optional]
            "nh3":  float,   # NH3 (µg/m³) [optional]
            
            # Optional context
            "temperature": float,  # °C
            "humidity": float,     # %
            "wind_speed": float,   # km/h
        }
    
    Returns
    -------
    dict
        {
            "aqi":           float,
            "category":      str,
            "health_advice": str,
        }
    """
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict, got {type(data).__name__}")
    
    bundle = _get_bundle()
    model = bundle['model']
    imputer = bundle['imputer']
    feature_cols = bundle['feature_cols']
    
    # Build feature vector
    row = {}
    
    # Geographic defaults (will be imputed if not provided)
    row['latitude'] = data.get('latitude', np.nan)
    row['longitude'] = data.get('longitude', np.nan)
    row['city_encoded'] = data.get('city_encoded', 0)
    row['state_encoded'] = data.get('state_encoded', 0)
    row['zone_encoded'] = data.get('zone_encoded', 0)
    row['population_million'] = data.get('population_million', np.nan)
    row['industrial_encoded'] = data.get('industrial_encoded', 1)  # Default to medium
    
    # Temporal defaults
    from datetime import datetime
    now = datetime.now()
    row['year'] = data.get('year', now.year)
    row['month'] = data.get('month', now.month)
    row['season_encoded'] = data.get('season_encoded', _get_season_code(now.month))
    
    # Pollutants (main predictors)
    row['pm25_ug_m3'] = data.get('pm25', data.get('pm2.5', np.nan))
    row['pm10_ug_m3'] = data.get('pm10', np.nan)
    row['no2_ug_m3'] = data.get('no2', np.nan)
    row['so2_ug_m3'] = data.get('so2', np.nan)
    row['co_mg_m3'] = data.get('co', np.nan)
    row['o3_ug_m3'] = data.get('o3', data.get('ozone', np.nan))
    row['nh3_ug_m3'] = data.get('nh3', np.nan)
    
    # Weather
    row['temperature_celsius'] = data.get('temperature', data.get('temp_c', np.nan))
    row['humidity_pct'] = data.get('humidity', np.nan)
    row['wind_speed_kmh'] = data.get('wind_speed', np.nan)
    row['rainfall_mm'] = data.get('rainfall', 0.0)
    row['visibility_km'] = data.get('visibility', np.nan)
    
    # Create DataFrame with only the features the model expects
    df = pd.DataFrame([row])
    
    # Select only features that exist in the model
    available_features = [f for f in feature_cols if f in df.columns]
    df_features = df[available_features]
    
    # Impute missing values
    df_imputed = pd.DataFrame(
        imputer.transform(df_features),
        columns=available_features
    )
    
    # Predict
    prediction = model.predict(df_imputed)
    aqi_value = round(float(prediction[0]), 2)
    
    # Ensure AQI is in valid range
    aqi_value = max(0, min(500, aqi_value))
    
    category, health_advice = _categorize(aqi_value)
    
    return {
        "aqi": aqi_value,
        "category": category,
        "health_advice": health_advice,
    }


def _get_season_code(month: int) -> int:
    """Get season code from month (0-3)."""
    if month in [12, 1, 2]:
        return 0  # Winter
    elif month in [3, 4, 5]:
        return 1  # Summer
    elif month in [6, 7, 8, 9]:
        return 2  # Monsoon
    else:
        return 3  # Post-Monsoon


# Backward compatibility - keep old function name
def predict_aqi_simple(pm25: float = None, pm10: float = None, 
                      no2: float = None, co: float = None, 
                      o3: float = None) -> dict:
    """
    Simple prediction interface (backward compatible).
    """
    data = {}
    if pm25 is not None:
        data['pm25'] = pm25
    if pm10 is not None:
        data['pm10'] = pm10
    if no2 is not None:
        data['no2'] = no2
    if co is not None:
        data['co'] = co
    if o3 is not None:
        data['o3'] = o3
    
    return predict_aqi(data)
