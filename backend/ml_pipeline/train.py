import pandas as pd
import numpy as np
import os
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score, f1_score

# Directory configuration
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, '..', '..', 'models_data', 'disaster_data.csv')
MODEL_DIR = os.path.join(BASE_DIR, '..', '..', 'models_data')
os.makedirs(MODEL_DIR, exist_ok=True)

def load_data():
    if not os.path.exists(DATA_PATH):
        print(f"ERROR: Dataset not found at {DATA_PATH}. Run data_generator.py first.")
        return None
    return pd.read_csv(DATA_PATH)

def train_severity_model(df):
    print("\n--- Training Severity Prediction Model ---")
    features = ['temp', 'rainfall', 'wind_speed', 'pop_density', 'historical_freq']
    X = df[features]
    y = df['severity']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Increased n_estimators and added max_depth for better generalization
    model = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    print(f"Model Accuracy: {acc:.4f}")
    print(f"Model F1-Score: {f1:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    model_path = os.path.join(MODEL_DIR, 'severity_model.joblib')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

def train_resource_model(df):
    print("\n--- Training Resource Demand Model ---")
    features = ['severity', 'pop_density', 'smoke_ppm'] # weather intensity proxied by smoke_ppm
    X = df[features]
    y = df[['ambulances', 'fire_trucks', 'rescue_boats']]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Model R2 Score: {r2:.4f}")
    print(f"Model MSE: {mse:.4f}")
    
    model_path = os.path.join(MODEL_DIR, 'resource_model.joblib')
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

def train_risk_prediction_model(df):
    print("\n--- Training Advanced Risk Prediction Model ---")
    features = ['temp', 'rainfall', 'pop_density', 'water_level', 'seismic_mag', 'smoke_ppm']
    X = df[features]
    y = df['risk_class']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    print(f"Model Accuracy: {acc:.4f}")
    print(f"Model F1-Score: {f1:.4f}")
    
    model_path = os.path.join(MODEL_DIR, 'risk_prediction_model.joblib')
    # Save model and metadata
    joblib.dump({
        'model': model,
        'features': features,
        'trained_at': datetime.now().isoformat(),
        'accuracy': acc,
        'f1_score': f1
    }, model_path)
    print(f"Advanced risk model saved to {model_path}")

if __name__ == "__main__":
    df = load_data()
    if df is not None:
        train_severity_model(df)
        train_resource_model(df)
        train_risk_prediction_model(df)
