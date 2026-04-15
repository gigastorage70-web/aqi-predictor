"""
predictor.py
------------
Backend-ready AQI prediction system.

Accepts a simplified pollutant dict, runs the model, and returns
AQI value + category + health advice.

Usage:
    from predictor import predict_aqi

    result = predict_aqi({
        "pm25": 95.0,
        "pm10": 180.0,
        "no2":  45.0,
        "co":   1.2,
        "o3":   60.0,
    })
    # {"aqi": 143.7, "category": "Unhealthy for Sensitive Groups", "health_advice": "..."}
"""

from __future__ import annotations

import streamlit as st
from model import load_model
from model import predict_aqi as _model_predict

# ---------------------------------------------------------------------------
# AQI scale (US EPA standard)
# ---------------------------------------------------------------------------

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
    # fallback (should never reach here)
    return _AQI_SCALE[-1][1], _AQI_SCALE[-1][2]


# ---------------------------------------------------------------------------
# Model cache — loaded once per server process, shared across all sessions
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Loading AQI model…")
def _get_bundle() -> dict:
    return load_model()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def predict_aqi(data: dict) -> dict:
    """
    Predict AQI from simplified pollutant readings.

    Parameters
    ----------
    data : dict
        {
            "pm25": float,   # PM2.5 average concentration (µg/m³)
            "pm10": float,   # PM10  average concentration (µg/m³)
            "no2":  float,   # NO2   average concentration (µg/m³)
            "co":   float,   # CO    average concentration (mg/m³)
            "o3":   float,   # Ozone average concentration (µg/m³)  [optional]
        }
        All keys are optional; missing values are median-imputed by the model.

    Returns
    -------
    dict
        {
            "aqi":           float,
            "category":      str,
            "health_advice": str,
        }

    Raises
    ------
    ValueError  – if `data` is not a dict or contains non-numeric values.
    """
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict, got {type(data).__name__}")

    # Map simplified keys → internal model keys (Avg_* format)
    key_map = {
        "pm25": "Avg_PM2.5",
        "pm10": "Avg_PM10",
        "no2":  "Avg_NO2",
        "co":   "Avg_CO",
        "o3":   "Avg_OZONE",   # stored as OZONE in the dataset
    }

    raw: dict = {}
    for user_key, model_key in key_map.items():
        value = data.get(user_key)
        if value is not None:
            try:
                raw[model_key] = float(value)
            except (TypeError, ValueError):
                raise ValueError(f"'{user_key}' must be numeric, got {value!r}")

    bundle = _get_bundle()
    aqi_value = round(_model_predict(raw, bundle=bundle), 2)
    category, health_advice = _categorize(aqi_value)

    return {
        "aqi":           aqi_value,
        "category":      category,
        "health_advice": health_advice,
    }
