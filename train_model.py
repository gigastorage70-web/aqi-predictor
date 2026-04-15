"""
train_csv_model.py
------------------
Train AQI prediction model using the new CSV dataset with health metrics.

Usage:
    python train_csv_model.py --csv air_quality_health_monthly.csv
"""

import argparse
import pickle
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

MODEL_PATH = "aqi_model.pkl"


def load_and_prepare_data(csv_path: str):
    """Load CSV and prepare features."""
    print(f"📂 Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"   Loaded {len(df)} records")
    print(f"   Columns: {df.columns.tolist()}")
    
    # Remove rows with missing AQI (target)
    df = df[df['aqi'].notna()].copy()
    print(f"   After removing missing AQI: {len(df)} records")
    
    return df


def engineer_features(df: pd.DataFrame):
    """Create features for the model."""
    print("\n🔧 Engineering features...")
    
    # Encode categorical variables
    le_city = LabelEncoder()
    le_state = LabelEncoder()
    le_zone = LabelEncoder()
    le_season = LabelEncoder()
    le_industrial = LabelEncoder()
    
    df['city_encoded'] = le_city.fit_transform(df['city'].astype(str))
    df['state_encoded'] = le_state.fit_transform(df['state'].astype(str))
    df['zone_encoded'] = le_zone.fit_transform(df['zone'].astype(str))
    df['season_encoded'] = le_season.fit_transform(df['season'].astype(str))
    df['industrial_encoded'] = le_industrial.fit_transform(df['industrialization'].astype(str))
    
    # Select features
    feature_cols = [
        # Geographic
        'latitude', 'longitude', 'city_encoded', 'state_encoded', 
        'zone_encoded', 'population_million', 'industrial_encoded',
        
        # Temporal
        'year', 'month', 'season_encoded',
        
        # Pollutants (primary predictors)
        'pm25_ug_m3', 'pm10_ug_m3', 'no2_ug_m3', 'so2_ug_m3', 
        'co_mg_m3', 'o3_ug_m3', 'nh3_ug_m3',
        
        # Weather
        'temperature_celsius', 'humidity_pct', 'wind_speed_kmh', 
        'rainfall_mm', 'visibility_km',
    ]
    
    # Check which features exist
    available_features = [f for f in feature_cols if f in df.columns]
    print(f"   Using {len(available_features)} features")
    
    X = df[available_features].copy()
    y = df['aqi'].copy()
    
    # Handle missing values
    imputer = SimpleImputer(strategy='median')
    X_imputed = pd.DataFrame(
        imputer.fit_transform(X),
        columns=available_features,
        index=X.index
    )
    
    print(f"   Features shape: {X_imputed.shape}")
    print(f"   Target shape: {y.shape}")
    print(f"   Missing values after imputation: {X_imputed.isnull().sum().sum()}")
    
    # Store encoders
    encoders = {
        'le_city': le_city,
        'le_state': le_state,
        'le_zone': le_zone,
        'le_season': le_season,
        'le_industrial': le_industrial,
        'imputer': imputer,
        'feature_cols': available_features
    }
    
    return X_imputed, y, encoders


def train_model(X, y):
    """Train the Gradient Boosting model."""
    print("\n🤖 Training model...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"   Training set: {X_train.shape}")
    print(f"   Test set: {X_test.shape}")
    
    # Train model
    model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        verbose=0
    )
    
    print("   Fitting model...")
    model.fit(X_train, y_train)
    
    # Evaluate
    print("\n📊 Model Performance:")
    
    # Training performance
    y_train_pred = model.predict(X_train)
    train_r2 = r2_score(y_train, y_train_pred)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
    print(f"   Training R²: {train_r2:.4f}")
    print(f"   Training RMSE: {train_rmse:.2f}")
    
    # Test performance
    y_test_pred = model.predict(X_test)
    test_r2 = r2_score(y_test, y_test_pred)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
    test_mae = mean_absolute_error(y_test, y_test_pred)
    
    print(f"   Test R²: {test_r2:.4f}")
    print(f"   Test RMSE: {test_rmse:.2f}")
    print(f"   Test MAE: {test_mae:.2f}")
    
    # Cross-validation
    print("\n   Running 5-fold cross-validation...")
    cv_scores = cross_val_score(
        model, X_train, y_train, cv=5, 
        scoring='r2', n_jobs=-1
    )
    print(f"   CV R² scores: {cv_scores}")
    print(f"   CV R² mean: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Feature importance
    print("\n🔍 Top 10 Feature Importances:")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        print(f"   {row['feature']}: {row['importance']:.4f}")
    
    return model, test_r2, test_rmse


def save_model(model, encoders, output_path: str):
    """Save model and preprocessing components."""
    print(f"\n💾 Saving model to {output_path}...")
    
    bundle = {
        'model': model,
        'imputer': encoders['imputer'],
        'le_city': encoders['le_city'],
        'le_state': encoders['le_state'],
        'le_zone': encoders['le_zone'],
        'le_season': encoders['le_season'],
        'le_industrial': encoders['le_industrial'],
        'feature_cols': encoders['feature_cols']
    }
    
    with open(output_path, 'wb') as f:
        pickle.dump(bundle, f)
    
    print(f"   ✅ Model saved successfully!")
    print(f"   File size: {round(os.path.getsize(output_path) / 1024 / 1024, 2)} MB")


def main():
    parser = argparse.ArgumentParser(description='Train AQI prediction model from CSV')
    parser.add_argument('--csv', default='data/air_quality_health_monthly.csv', 
                       help='Path to CSV file')
    parser.add_argument('--output', default=MODEL_PATH, help='Output model path')
    args = parser.parse_args()
    
    print("=" * 80)
    print("🌍 AQI Model Training - CSV Dataset")
    print("=" * 80)
    
    # Load data
    df = load_and_prepare_data(args.csv)
    
    # Engineer features
    X, y, encoders = engineer_features(df)
    
    # Train model
    model, r2, rmse = train_model(X, y)
    
    # Save model
    save_model(model, encoders, args.output)
    
    print("\n" + "=" * 80)
    print("✅ Training Complete!")
    print(f"   Model Performance: R² = {r2:.4f}, RMSE = {rmse:.2f}")
    print(f"   Model saved to: {args.output}")
    print("=" * 80)
    
    # Test prediction
    print("\n🧪 Testing prediction...")
    sample = X.iloc[0:1]
    pred = model.predict(sample)
    actual = y.iloc[0]
    print(f"   Sample prediction: {pred[0]:.2f}")
    print(f"   Actual AQI: {actual:.2f}")
    print(f"   Error: {abs(pred[0] - actual):.2f}")


if __name__ == "__main__":
    main()
