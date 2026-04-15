"""
train_and_save.py
-----------------
Run this ONCE to train the model and persist it as aqi_model.pkl.
After that, use model.py for all predictions.

Usage:
    python train_and_save.py --xml path/to/data_aqi_cpcb.xml
"""

import argparse
import csv
import pickle
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder

MODEL_PATH = "aqi_model.pkl"


# ---------------------------------------------------------------------------
# 1. Parse XML → CSV-like DataFrame
# ---------------------------------------------------------------------------

def parse_xml(xml_path: str) -> pd.DataFrame:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    rows = []
    for country in root.findall("Country"):
        country_id = country.get("id")
        for state in country.findall("State"):
            state_id = state.get("id")
            for city in state.findall("City"):
                city_id = city.get("id")
                for station in city.findall("Station"):
                    lat       = station.get("latitude")
                    lon       = station.get("longitude")
                    last_upd  = station.get("lastupdate")

                    aqi_value, predominant = "", ""
                    aqi_elem = station.find("Air_Quality_Index")
                    if aqi_elem is not None:
                        aqi_value    = aqi_elem.get("Value", "")
                        predominant  = aqi_elem.get("Predominant_Parameter", "")

                    for pollutant in station.findall("Pollutant_Index"):
                        rows.append({
                            "Country":               country_id,
                            "State":                 state_id,
                            "City":                  city_id,
                            "Station":               station.get("id"),
                            "Latitude":              lat,
                            "Longitude":             lon,
                            "Last Update":           last_upd,
                            "Pollutant":             pollutant.get("id"),
                            "Min":                   pollutant.get("Min"),
                            "Max":                   pollutant.get("Max"),
                            "Avg":                   pollutant.get("Avg"),
                            "AQI":                   aqi_value,
                            "Predominant Parameter": predominant,
                        })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. Preprocess
# ---------------------------------------------------------------------------

def build_features(df: pd.DataFrame):
    numeric_cols = ["Min", "Max", "Avg", "AQI", "Latitude", "Longitude"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Last Update"] = pd.to_datetime(df["Last Update"], errors="coerce")
    df["Hour"]      = df["Last Update"].dt.hour
    df["Day"]       = df["Last Update"].dt.day
    df["Month"]     = df["Last Update"].dt.month
    df["DayOfWeek"] = df["Last Update"].dt.dayofweek

    # Pivot pollutants into columns
    pivot = df.pivot_table(
        index=["Country", "State", "City", "Station", "Latitude", "Longitude",
               "Last Update", "AQI", "Predominant Parameter",
               "Hour", "Day", "Month", "DayOfWeek"],
        columns="Pollutant",
        values=["Min", "Max", "Avg"],
        aggfunc="first",
    ).reset_index()

    pivot.columns = [
        "_".join(col).strip("_") if col[1] else col[0]
        for col in pivot.columns.values
    ]

    # Drop rows with missing target
    pivot = pivot[pivot["AQI"].notna()].copy()

    # Encode categoricals
    le_state = LabelEncoder()
    le_city  = LabelEncoder()
    le_pred  = LabelEncoder()

    pivot["State_Encoded"]       = le_state.fit_transform(pivot["State"].astype(str))
    pivot["City_Encoded"]        = le_city.fit_transform(pivot["City"].astype(str))
    pivot["Predominant_Encoded"] = le_pred.fit_transform(
        pivot["Predominant Parameter"].astype(str)
    )

    # Range features
    for p in ["PM2.5", "PM10", "NO2", "SO2", "CO"]:
        mn_col = f"Min_{p}"
        mx_col = f"Max_{p}"
        if mn_col in pivot.columns and mx_col in pivot.columns:
            pivot[f"{p}_Range"] = pivot[mx_col] - pivot[mn_col]

    feature_cols = [
        "Latitude", "Longitude", "State_Encoded", "City_Encoded",
        "Hour", "Day", "Month", "DayOfWeek",
        "Avg_PM2.5", "Min_PM2.5", "Max_PM2.5", "PM2.5_Range",
        "Avg_PM10",  "Min_PM10",  "Max_PM10",  "PM10_Range",
        "Avg_NO2",   "Min_NO2",   "Max_NO2",   "NO2_Range",
        "Avg_SO2",   "Min_SO2",   "Max_SO2",   "SO2_Range",
        "Avg_CO",    "Min_CO",    "Max_CO",    "CO_Range",
        "Predominant_Encoded",
    ]

    X = pivot[feature_cols].copy()
    y = pivot["AQI"].copy()

    imputer = SimpleImputer(strategy="median")
    X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=feature_cols)

    return X_imputed, y, imputer, le_state, le_city, le_pred


# ---------------------------------------------------------------------------
# 3. Train & save
# ---------------------------------------------------------------------------

def train_and_save(xml_path: str, output_path: str = MODEL_PATH):
    print(f"Parsing XML: {xml_path}")
    df = parse_xml(xml_path)
    print(f"  Raw rows: {len(df)}")

    print("Building features...")
    X, y, imputer, le_state, le_city, le_pred = build_features(df)
    print(f"  Training samples: {len(X)}, features: {X.shape[1]}")

    print("Training GradientBoostingRegressor...")
    model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    bundle = {
        "model":    model,
        "imputer":  imputer,
        "le_state": le_state,
        "le_city":  le_city,
        "le_pred":  le_pred,
    }

    with open(output_path, "wb") as f:
        pickle.dump(bundle, f)

    print(f"Model saved to {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--xml", required=True, help="Path to data_aqi_cpcb.xml")
    parser.add_argument("--out", default=MODEL_PATH, help="Output .pkl path")
    args = parser.parse_args()
    train_and_save(args.xml, args.out)
