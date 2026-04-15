"""
AQI Prediction Module
---------------------
Production-ready module for predicting Air Quality Index (AQI)
using a pre-trained Gradient Boosting model.
"""

import pickle
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer

MODEL_PATH = "aqi_model.pkl"

# Feature columns expected by the model (in order)
FEATURE_COLS = [
    'Latitude', 'Longitude', 'State_Encoded', 'City_Encoded',
    'Hour', 'Day', 'Month', 'DayOfWeek',
    'Avg_PM2.5', 'Min_PM2.5', 'Max_PM2.5', 'PM2.5_Range',
    'Avg_PM10', 'Min_PM10', 'Max_PM10', 'PM10_Range',
    'Avg_NO2', 'Min_NO2', 'Max_NO2', 'NO2_Range',
    'Avg_SO2', 'Min_SO2', 'Max_SO2', 'SO2_Range',
    'Avg_CO', 'Min_CO', 'Max_CO', 'CO_Range',
    'Predominant_Encoded',
]


def load_model(path: str = MODEL_PATH) -> dict:
    """
    Load the saved model bundle from disk.

    Parameters
    ----------
    path : str
        Path to the .pkl file produced by train_and_save.py

    Returns
    -------
    dict with keys:
        'model'    – trained GradientBoostingRegressor
        'imputer'  – fitted SimpleImputer
        'le_state' – fitted LabelEncoder for State
        'le_city'  – fitted LabelEncoder for City
        'le_pred'  – fitted LabelEncoder for Predominant Parameter
    """
    with open(path, "rb") as f:
        bundle = pickle.load(f)
    return bundle


def preprocess_input(raw: dict, bundle: dict) -> pd.DataFrame:
    """
    Convert a raw input dict into a model-ready DataFrame.

    Expected keys in `raw` (all optional – missing values are imputed):
        Latitude, Longitude, State, City,
        Hour, Day, Month, DayOfWeek,
        Avg_PM2.5, Min_PM2.5, Max_PM2.5,
        Avg_PM10,  Min_PM10,  Max_PM10,
        Avg_NO2,   Min_NO2,   Max_NO2,
        Avg_SO2,   Min_SO2,   Max_SO2,
        Avg_CO,    Min_CO,    Max_CO,
        Predominant_Parameter

    Parameters
    ----------
    raw    : dict  – one observation
    bundle : dict  – model bundle returned by load_model()

    Returns
    -------
    pd.DataFrame with exactly the columns in FEATURE_COLS, imputed.
    """
    le_state = bundle["le_state"]
    le_city  = bundle["le_city"]
    le_pred  = bundle["le_pred"]
    imputer  = bundle["imputer"]

    row = {}

    # --- geographic ---
    row["Latitude"]  = raw.get("Latitude",  np.nan)
    row["Longitude"] = raw.get("Longitude", np.nan)

    # Label-encode State / City / Predominant Parameter
    # Unknown labels fall back to 0 (safe default)
    def safe_encode(encoder, value):
        if value is None:
            return np.nan
        try:
            return int(encoder.transform([str(value)])[0])
        except ValueError:
            return 0

    row["State_Encoded"]       = safe_encode(le_state, raw.get("State"))
    row["City_Encoded"]        = safe_encode(le_city,  raw.get("City"))
    row["Predominant_Encoded"] = safe_encode(le_pred,  raw.get("Predominant_Parameter"))

    # --- temporal ---
    for col in ("Hour", "Day", "Month", "DayOfWeek"):
        row[col] = raw.get(col, np.nan)

    # --- pollutants ---
    pollutants = ["PM2.5", "PM10", "NO2", "SO2", "CO"]
    for p in pollutants:
        avg = raw.get(f"Avg_{p}", np.nan)
        mn  = raw.get(f"Min_{p}", np.nan)
        mx  = raw.get(f"Max_{p}", np.nan)
        row[f"Avg_{p}"] = avg
        row[f"Min_{p}"] = mn
        row[f"Max_{p}"] = mx
        # Range: compute if both bounds available, else NaN
        if not (np.isnan(float(mx)) if mx is None else np.isnan(mx)) and \
           not (np.isnan(float(mn)) if mn is None else np.isnan(mn)):
            row[f"{p}_Range"] = float(mx) - float(mn)
        else:
            row[f"{p}_Range"] = np.nan

    df = pd.DataFrame([row])[FEATURE_COLS]
    df_imputed = pd.DataFrame(
        imputer.transform(df),
        columns=FEATURE_COLS,
    )
    return df_imputed


def predict_aqi(raw_input: dict, bundle: dict = None, model_path: str = MODEL_PATH) -> float:
    """
    Predict AQI for a single observation.

    Parameters
    ----------
    raw_input  : dict  – raw feature values (see preprocess_input for keys)
    bundle     : dict  – pre-loaded model bundle (optional; loaded from disk if None)
    model_path : str   – path to .pkl file (used only when bundle is None)

    Returns
    -------
    float – predicted AQI value
    """
    if bundle is None:
        bundle = load_model(model_path)

    X = preprocess_input(raw_input, bundle)
    prediction = bundle["model"].predict(X)
    return float(prediction[0])
