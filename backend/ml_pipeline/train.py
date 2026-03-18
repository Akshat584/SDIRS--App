import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib
import os

# Create directory for models if it doesn't exist
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'models_data')
os.makedirs(MODEL_DIR, exist_ok=True)

def train_severity_model():
    print("Training Severity Prediction Model...")
    # Synthetic data: [temp, rainfall, wind_speed, pop_density, historical_freq]
    # Severity: 0: Low, 1: Medium, 2: High, 3: Critical
    X = np.array([
        [25, 10, 5, 100, 1], [30, 50, 20, 500, 2], [35, 150, 60, 2000, 5], [40, 300, 120, 5000, 10],
        [20, 5, 2, 50, 1], [28, 40, 15, 400, 2], [32, 120, 50, 1500, 4], [38, 250, 100, 4000, 8],
        [22, 15, 8, 150, 1], [26, 60, 25, 600, 3], [33, 140, 55, 1800, 5], [42, 280, 110, 4500, 9]
    ])
    y = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3])
    
    # Add some noise to make it slightly more "real"
    for _ in range(10):
        X = np.vstack([X, X + np.random.normal(0, 1, X.shape)])
        y = np.concatenate([y, y])

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    model_path = os.path.join(MODEL_DIR, 'severity_model.joblib')
    joblib.dump(model, model_path)
    print(f"Severity model saved to {model_path}")

def train_resource_model():
    print("Training Resource Demand Model...")
    # Synthetic data: [predicted_severity (0-3), pop_density, weather_intensity (0-100)]
    # Output: [ambulances, fire_trucks, rescue_boats]
    X = np.array([
        [0, 100, 10], [1, 500, 40], [2, 2000, 70], [3, 5000, 95],
        [0, 200, 15], [1, 600, 45], [2, 1800, 75], [3, 4500, 90],
        [1, 1000, 50], [2, 3000, 80], [3, 6000, 100], [0, 50, 5]
    ])
    y = np.array([
        [1, 0, 0], [2, 1, 0], [5, 3, 2], [10, 8, 5],
        [1, 0, 0], [3, 2, 1], [6, 4, 3], [12, 10, 6],
        [4, 2, 1], [8, 6, 4], [15, 12, 8], [0, 0, 0]
    ])

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    model_path = os.path.join(MODEL_DIR, 'resource_model.joblib')
    joblib.dump(model, model_path)
    print(f"Resource model saved to {model_path}")

def train_advanced_risk_model():
    print("Training Advanced Risk Prediction Model (Weather + IoT Fusion)...")
    # Features: [temp, rainfall, pop_density, water_level, seismic_mag, smoke_ppm]
    # Risk Class: 0: Low, 1: Medium, 2: High, 3: Critical
    X = np.array([
        [25, 10, 100, 0.5, 0.1, 15], [30, 50, 500, 1.2, 0.2, 30],
        [35, 150, 2000, 3.5, 1.5, 80], [40, 300, 5000, 5.0, 4.5, 400], # Critical
        [20, 5, 50, 0.3, 0.0, 10], [28, 40, 400, 1.0, 0.1, 25],
        [32, 120, 1500, 2.8, 0.8, 60], [38, 250, 4000, 4.5, 3.8, 300], # High/Crit
        [15, 0, 30, 0.2, 0.0, 5], [26, 60, 600, 1.5, 0.3, 35],
        [33, 140, 1800, 3.2, 1.2, 90], [42, 320, 5500, 5.5, 4.8, 450] # Critical
    ])
    y = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3])

    # Augment data
    for _ in range(15):
        X = np.vstack([X, X + np.random.normal(0, 0.5, X.shape)])
        y = np.concatenate([y, y])

    model = RandomForestClassifier(n_estimators=150, random_state=42)
    model.fit(X, y)
    
    model_path = os.path.join(MODEL_DIR, 'risk_prediction_model.joblib')
    # Save model and metadata
    joblib.dump({
        'model': model,
        'features': ['temp', 'rainfall', 'pop_density', 'water_level', 'seismic_mag', 'smoke_ppm'],
        'trained_at': datetime.now().isoformat()
    }, model_path)
    print(f"Advanced risk model saved to {model_path}")

if __name__ == "__main__":
    from datetime import datetime
    train_severity_model()
    train_resource_model()
    train_advanced_risk_model()
