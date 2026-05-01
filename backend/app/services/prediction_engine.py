import os
import joblib
import numpy as np
import httpx
import logging
from datetime import datetime
from typing import List, Dict, Optional
from app.models.prediction import DisasterRisk, PredictionResponse
from app.services.iot_sensor_service import iot_service
from app.services.population_service import population_service
from app.services.data_validator import data_validator
from app.core.config import settings

logger = logging.getLogger("SDIRS_Prediction")

# Path to models
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'models_data', 'risk_prediction_model.joblib')

# USGS and Weather API endpoints
USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"


class PredictionEngine:
    """
    SDIRS Advanced Prediction Engine (Module 1)
    Uses a trained Random Forest model to analyze Weather + IoT + Population data.
    Provides high-precision risk probabilities.
    """

    _model_data = None
    _cached_weather: Optional[dict] = None
    _weather_cache_time: Optional[datetime] = None

    @classmethod
    def _load_model(cls):
        if cls._model_data is None:
            if os.path.exists(MODEL_PATH):
                try:
                    cls._model_data = joblib.load(MODEL_PATH)
                    logger.info(f"SDIRS AI: Risk Model loaded from {MODEL_PATH}")
                except Exception as e:
                    logger.warning(f"SDIRS AI: Error loading model: {e}")
            else:
                logger.info("SDIRS AI: Risk model not found. Using data-driven prediction.")
        return cls._model_data

    @classmethod
    async def _fetch_weather_data(cls, lat: float, lon: float) -> dict:
        """
        Fetches real weather data from OpenWeatherMap API.
        Falls back to NWS API if OpenWeatherMap key is not configured.
        """
        # Check if we have a valid API key
        api_key = settings.openweathermap_api_key
        if not api_key or api_key in ("YOUR_OPENWEATHERMAP_API_KEY", ""):
            # Try NWS as fallback
            return await cls._fetch_nws_alerts(lat, lon)

        try:
            # Fetch current weather from OpenWeatherMap
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Current weather
                weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
                resp = await client.get(weather_url)
                resp.raise_for_status()
                weather_data = resp.json()

                # Forecast (for rainfall prediction)
                forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
                forecast_resp = await client.get(forecast_url)
                forecast_data = forecast_resp.json() if forecast_resp.status_code == 200 else {}

                return {
                    "temp": weather_data.get("main", {}).get("temp", 20.0),
                    "humidity": weather_data.get("main", {}).get("humidity", 50),
                    "rainfall": cls._calculate_rainfall(forecast_data),
                    "wind_speed": weather_data.get("wind", {}).get("speed", 0),
                    "description": weather_data.get("weather", [{}])[0].get("description", "unknown"),
                    "source": "OpenWeatherMap"
                }
        except Exception as e:
            logger.warning(f"Failed to fetch weather from OpenWeatherMap: {e}")
            return await cls._fetch_nws_alerts(lat, lon)

    @classmethod
    async def _fetch_nws_alerts(cls, lat: float, lon: float) -> dict:
        """
        Fetches weather alerts from NWS (National Weather Service) - Free, no API key required.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get forecast metadata
                points_url = f"https://api.weather.gov/points/{lat},{lon}"
                points_resp = await client.get(points_url)
                if points_resp.status_code != 200:
                    return cls._get_default_weather()

                points_data = points_resp.json()
                forecast_url = points_data.get("properties", {}).get("forecast", "")
                alerts_url = points_data.get("properties", {}).get("alerts", "")

                # Get forecast
                forecast_data = {}
                if forecast_url:
                    forecast_resp = await client.get(forecast_url)
                    if forecast_resp.status_code == 200:
                        forecast_data = forecast_resp.json()

                # Get alerts
                alerts_data = []
                if alerts_url:
                    alerts_resp = await client.get(alerts_url)
                    if alerts_resp.status_code == 200:
                        alerts_data = alerts_resp.json().get("features", [])

                # Calculate rainfall from forecast
                rainfall = cls._calculate_rainfall_from_nws(forecast_data)

                # Check for active alerts
                has_flood_alert = any("Flood" in a.get("properties", {}).get("event", "") for a in alerts_data)
                has_severe_alert = any("Warning" in a.get("properties", {}).get("event", "") for a in alerts_data)

                return {
                    "temp": 20.0,  # Default, NWS doesn't provide current temp in this endpoint
                    "humidity": 60,
                    "rainfall": rainfall,
                    "wind_speed": 10.0,
                    "description": "From NWS alerts" if alerts_data else "clear",
                    "has_flood_alert": has_flood_alert,
                    "has_severe_alert": has_severe_alert,
                    "alerts": alerts_data,
                    "source": "NWS"
                }
        except Exception as e:
            logger.warning(f"Failed to fetch NWS data: {e}")
            return cls._get_default_weather()

    @staticmethod
    def _calculate_rainfall(forecast_data: dict) -> float:
        """Calculate total rainfall from OpenWeatherMap forecast."""
        try:
            periods = forecast_data.get("list", [])[:8]  # Next ~24 hours
            total_rain = sum(p.get("rain", {}).get("3h", 0) for p in periods)
            return total_rain
        except:
            return 0.0

    @staticmethod
    def _calculate_rainfall_from_nws(forecast_data: dict) -> float:
        """Calculate rainfall probability from NWS forecast."""
        try:
            periods = forecast_data.get("properties", {}).get("periods", [])[:8]
            # Use qpf (Quantitative Precipitation Forecast) if available
            total = sum(p.get("quantitativePrecipitation", {}).get("value", 0) or 0 for p in periods)
            # Or use probability of precipitation
            if total == 0:
                total = sum(p.get("probabilityOfPrecipitation", {}).get("value", 0) or 0 for p in periods) / 100 * 10
            return total
        except:
            return 0.0

    @staticmethod
    def _get_default_weather() -> dict:
        """Return default weather values when API calls fail."""
        return {
            "temp": 20.0,
            "humidity": 50,
            "rainfall": 0.0,
            "wind_speed": 5.0,
            "description": "no data",
            "source": "default"
        }

    @staticmethod
    def _validate_coordinates(lat: float, lon: float) -> bool:
        """Validate latitude and longitude values."""
        return -90 <= lat <= 90 and -180 <= lon <= 180

    @staticmethod
    async def get_disaster_risks(lat: float, lon: float) -> PredictionResponse:
        """
        Calculate disaster risks using real weather data and ML model.
        """
        # Validate coordinates
        if not PredictionEngine._validate_coordinates(lat, lon):
            logger.warning(f"Invalid coordinates: lat={lat}, lon={lon}")
            lat = max(-90, min(90, lat))  # Clamp to valid range
            lon = max(-180, min(180, lon))

        model_data = PredictionEngine._load_model()
        nearby_sensors = iot_service.get_nearby_sensor_data(lat, lon)

        # Fetch REAL weather data
        weather_data = await PredictionEngine._fetch_weather_data(lat, lon)

        # Use real weather data for features
        temp = weather_data.get("temp", 20.0)
        rainfall = weather_data.get("rainfall", 0.0)
        humidity = weather_data.get("humidity", 50)

        # Fetch REAL population density from Census API
        pop_density = await population_service.get_population_density(lat, lon)

        # Get IoT sensor data (simulated but represents real readings)
        water_val = next((s.current_value for s in nearby_sensors if s.type == "water_level"), 0.5)
        seismic_val = next((s.current_value for s in nearby_sensors if s.type == "seismic"), 0.1)
        smoke_val = next((s.current_value for s in nearby_sensors if s.type == "smoke"), 20.0)

        risks = []

        if model_data:
            # Use the trained Random Forest model for prediction
            features = np.array([[temp, rainfall, pop_density, water_val, seismic_val, smoke_val]])
            model = model_data['model']

            # Predict Risk Class (0-3) and Probabilities
            risk_class = int(model.predict(features)[0])
            probs = model.predict_proba(features)[0]

            final_prob = float(probs[risk_class])

            levels = ["low", "medium", "high", "critical"]
            risk_level = levels[risk_class]

            # Adjust based on real weather conditions
            if rainfall > 10:
                risk_level = "high" if risk_level in ["low", "medium"] else risk_level
            if weather_data.get("has_flood_alert"):
                risk_level = "critical"

            # 1. Flood Risk
            risks.append(DisasterRisk(
                disaster_type="Flood",
                probability=round(min(final_prob * (water_val / 1.0) * (1 + rainfall / 100), 1.0), 2),
                alert_level=risk_level if water_val > 2.0 or rainfall > 20 else "low",
                area=f"Zone {int(lat)}",
                recommendations=[
                    f"Current rainfall: {rainfall}mm",
                    f"Water level: {water_val}m",
                    f"Weather source: {weather_data.get('source', 'N/A')}"
                ]
            ))

            # 2. Fire Risk
            risks.append(DisasterRisk(
                disaster_type="Wildfire",
                probability=round(min(final_prob * (smoke_val / 100.0) * (1 - humidity / 200), 1.0), 2),
                alert_level=risk_level if smoke_val > 100.0 and humidity < 40 else "low",
                area=f"Forest Sector {int(lon)}",
                recommendations=[
                    f"Humidity: {humidity}%",
                    f"Smoke level: {smoke_val}ppm",
                    f"Conditions: {weather_data.get('description', 'unknown')}"
                ]
            ))

            # 3. Seismic Risk
            if seismic_val > 0.5:
                risks.append(DisasterRisk(
                    disaster_type="Seismic Activity",
                    probability=min(1.0, seismic_val / 5.0),
                    alert_level=risk_level if seismic_val > 3.0 else "medium",
                    area=f"Seismic Fault {int(lat)}",
                    recommendations=[
                        "Drop, Cover, and Hold on",
                        f"Magnitude: {seismic_val}"
                    ]
                ))
        else:
            # Fallback: Rule-based prediction when model not available
            # Uses real weather data but no ML

            # Flood risk from rainfall
            flood_prob = min(1.0, rainfall / 50)
            if water_val > 2:
                flood_prob = min(1.0, flood_prob + 0.3)

            # Fire risk from humidity and smoke
            fire_prob = max(0, (100 - humidity) / 100) * min(1.0, smoke_val / 100)

            risks.append(DisasterRisk(
                disaster_type="Flood",
                probability=round(flood_prob, 2),
                alert_level="critical" if flood_prob > 0.7 else "high" if flood_prob > 0.4 else "low",
                area=f"Zone {int(lat)}",
                recommendations=[f"Rainfall: {rainfall}mm from {weather_data.get('source')}"]
            ))

            if humidity < 50:
                risks.append(DisasterRisk(
                    disaster_type="Wildfire",
                    probability=round(fire_prob, 2),
                    alert_level="high" if fire_prob > 0.5 else "medium" if fire_prob > 0.2 else "low",
                    area=f"Forest Sector {int(lon)}",
                    recommendations=[f"Low humidity: {humidity}%"]
                ))

            if seismic_val > 0.5:
                risks.append(DisasterRisk(
                    disaster_type="Seismic Activity",
                    probability=min(1.0, seismic_val / 5.0),
                    alert_level="high" if seismic_val > 3.0 else "medium",
                    area=f"Seismic Fault {int(lat)}",
                    recommendations=[f"Magnitude: {seismic_val}"]
                ))

        return PredictionResponse(
            location={"lat": lat, "lon": lon},
            timestamp=datetime.now(),
            risks=risks
        )
