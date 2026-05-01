"""
ML Training Pipeline for SDIRS
Collects historical disaster data and trains prediction models.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import json

import numpy as np
import httpx

logger = logging.getLogger("SDIRS_ML_Pipeline")

@dataclass
class TrainingSample:
    """A single training sample for the ML model."""
    features: np.ndarray
    label: int  # 0=low, 1=medium, 2=high, 3=critical
    timestamp: datetime
    location: Tuple[float, float]

class MLTrainingPipeline:
    """
    ML Training Pipeline for disaster risk prediction.
    Collects historical data and trains/updates prediction models.
    """

    # Feature columns
    FEATURE_NAMES = [
        "temperature", "humidity", "rainfall", "wind_speed",
        "population_density", "water_level", "seismic", "smoke",
        "proximity_to_water", "proximity_to_faults"
    ]

    # API endpoints for historical data
    NOAA_HISTORICAL_URL = "https://www.ncdc.noaa.gov/cdo-web/api/v2/data"
    USGS_ARCHIVE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    def __init__(self):
        self.model_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'models_data', 'risk_prediction_model.joblib'
        )
        self.training_data_path = os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 'models_data', 'training_data.json'
        )
        self._training_samples: List[TrainingSample] = []

    async def collect_historical_weather(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Collect historical weather data from NOAA/CDO API.
        Note: Requires NOAA token for full access.
        """
        # This would use NOAA Climate Data Online API
        # For now, returns empty list as placeholder
        logger.info(f"Collecting historical weather from {start_date} to {end_date}")
        return []

    async def collect_historical_earthquakes(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Collect historical earthquake data from USGS archive."""
        try:
            params = {
                "format": "geojson",
                "starttime": start_date.isoformat(),
                "endtime": end_date.isoformat(),
                "minmagnitude": 4.0
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(self.USGS_ARCHIVE_URL, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    features = data.get("features", [])
                    logger.info(f"Collected {len(features)} historical earthquakes")
                    return features
        except Exception as e:
            logger.error(f"Failed to collect earthquakes: {e}")

        return []

    def load_existing_training_data(self) -> int:
        """Load existing training data from file."""
        if not os.path.exists(self.training_data_path):
            return 0

        try:
            with open(self.training_data_path, 'r') as f:
                data = json.load(f)

            for item in data.get("samples", []):
                features = np.array(item["features"])
                label = item["label"]
                timestamp = datetime.fromisoformat(item["timestamp"])
                location = tuple(item["location"])

                self._training_samples.append(TrainingSample(
                    features=features,
                    label=label,
                    timestamp=timestamp,
                    location=location
                ))

            logger.info(f"Loaded {len(self._training_samples)} training samples")
            return len(self._training_samples)
        except Exception as e:
            logger.error(f"Failed to load training data: {e}")
            return 0

    def add_training_sample(self, features: List[float], label: int, location: Tuple[float, float]):
        """Add a single training sample."""
        sample = TrainingSample(
            features=np.array(features),
            label=label,
            timestamp=datetime.now(),
            location=location
        )
        self._training_samples.append(sample)

    def save_training_data(self) -> bool:
        """Save training data to file."""
        try:
            os.makedirs(os.path.dirname(self.training_data_path), exist_ok=True)

            data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "sample_count": len(self._training_samples),
                "samples": [
                    {
                        "features": sample.features.tolist(),
                        "label": sample.label,
                        "timestamp": sample.timestamp.isoformat(),
                        "location": list(sample.location)
                    }
                    for sample in self._training_samples
                ]
            }

            with open(self.training_data_path, 'w') as f:
                json.dump(data, f)

            logger.info(f"Saved {len(self._training_samples)} training samples")
            return True
        except Exception as e:
            logger.error(f"Failed to save training data: {e}")
            return False

    def create_training_dataset(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create feature matrix and labels from collected samples.
        """
        if not self._training_samples:
            logger.warning("No training samples available")
            return np.array([]), np.array([])

        X = np.array([s.features for s in self._training_samples])
        y = np.array([s.label for s in self._training_samples])

        logger.info(f"Created training dataset: X.shape={X.shape}, y.shape={y.shape}")
        return X, y

    def train_model(self, X: np.ndarray, y: np.ndarray) -> Optional[Any]:
        """
        Train a Random Forest model on the collected data.
        """
        if len(X) < 10:
            logger.warning(f"Insufficient training samples: {len(X)}")
            return None

        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.model_selection import cross_val_score

            # Train Random Forest
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )

            model.fit(X, y)

            # Cross-validation score
            cv_scores = cross_val_score(model, X, y, cv=5)
            logger.info(f"Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump({'model': model, 'feature_names': self.FEATURE_NAMES}, self.model_path)
            logger.info(f"Model saved to {self.model_path}")

            return model
        except ImportError:
            logger.error("scikit-learn not installed")
            return None
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return None

    def evaluate_model(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model performance on test data.
        """
        if not os.path.exists(self.model_path):
            return {"error": "Model not found"}

        try:
            model_data = joblib.load(self.model_path)
            model = model_data['model']

            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

            y_pred = model.predict(X_test)

            return {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, average='weighted'),
                "recall": recall_score(y_test, y_pred, average='weighted'),
                "f1_score": f1_score(y_test, y_pred, average='weighted')
            }
        except Exception as e:
            logger.error(f"Model evaluation failed: {e}")
            return {"error": str(e)}

    def generate_synthetic_training_data(self, n_samples: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic training data for initial model training.
        This creates realistic disaster scenarios for the model to learn from.
        """
        logger.info(f"Generating {n_samples} synthetic training samples...")

        np.random.seed(42)

        samples = []
        labels = []

        for _ in range(n_samples):
            # Generate features
            temp = np.random.normal(25, 15)  # Temperature: mean 25C, std 15
            humidity = np.random.uniform(20, 100)
            rainfall = np.random.exponential(10)  # Most rainfall values small
            wind_speed = np.random.exponential(5)
            pop_density = np.random.uniform(100, 10000)
            water_level = np.random.exponential(2)
            seismic = np.random.exponential(0.5)
            smoke = np.random.exponential(50)
            proximity_water = np.random.uniform(0, 50)  # km
            proximity_faults = np.random.uniform(0, 100)  # km

            features = [
                temp, humidity, rainfall, wind_speed,
                pop_density, water_level, seismic, smoke,
                proximity_water, proximity_faults
            ]

            # Determine label based on risk factors
            risk_score = 0

            # High rainfall = flood risk
            if rainfall > 30:
                risk_score += 2
            elif rainfall > 15:
                risk_score += 1

            # High water level = flood
            if water_level > 4:
                risk_score += 2
            elif water_level > 2:
                risk_score += 1

            # Low humidity + high smoke = fire
            if humidity < 30 and smoke > 100:
                risk_score += 2
            elif humidity < 50 and smoke > 50:
                risk_score += 1

            # High seismic = earthquake
            if seismic > 3:
                risk_score += 3
            elif seismic > 1:
                risk_score += 1

            # High population = higher impact
            if pop_density > 5000:
                risk_score += 1

            # Convert to label (0-3)
            label = min(3, risk_score)

            samples.append(features)
            labels.append(label)

        X = np.array(samples)
        y = np.array(labels)

        logger.info(f"Generated dataset: {X.shape}, class distribution: {np.bincount(y)}")
        return X, y


# Global singleton
ml_pipeline = MLTrainingPipeline()
