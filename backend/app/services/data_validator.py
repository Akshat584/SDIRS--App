"""
Data Validation Layer for SDIRS
Validates incoming data from external APIs and sensors before ML processing.
"""
import logging
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger("SDIRS_DataValidator")

@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    message: str
    corrected_value: Optional[Any] = None

class DataValidator:
    """
    Validates data from external APIs and sensors.
    Ensures data quality before ML processing.
    """

    # Physical limits for sensor readings
    SENSOR_LIMITS = {
        "seismic": {"min": 0.0, "max": 9.9, "unit": "Richter scale"},
        "water_level": {"min": 0.0, "max": 20.0, "unit": "meters"},
        "smoke": {"min": 0.0, "max": 10000.0, "unit": "PPM"},
        "temperature": {"min": -50.0, "max": 60.0, "unit": "celsius"},
        "humidity": {"min": 0.0, "max": 100.0, "unit": "percentage"},
        "wind_speed": {"min": 0.0, "max": 120.0, "unit": "m/s"},
        "rainfall": {"min": 0.0, "max": 500.0, "unit": "mm"},
        "pressure": {"min": 800.0, "max": 1100.0, "unit": "hPa"},
    }

    # Weather data validity window
    CACHE_VALIDITY_MINUTES = 30

    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> ValidationResult:
        """Validate geographic coordinates."""
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            return ValidationResult(False, "Coordinates must be numeric")

        if not (-90 <= lat <= 90):
            return ValidationResult(False, f"Latitude {lat} out of range [-90, 90]")

        if not (-180 <= lon <= 180):
            return ValidationResult(False, f"Longitude {lon} out of range [-180, 180]")

        return ValidationResult(True, "Valid coordinates")

    @staticmethod
    def validate_weather(weather: dict) -> ValidationResult:
        """Validate weather data from OpenWeatherMap/NWS."""
        if not weather:
            return ValidationResult(False, "Empty weather data")

        errors = []

        # Temperature validation
        temp = weather.get("temp")
        if temp is not None:
            if temp < -100 or temp > 60:
                errors.append(f"Temperature {temp}°C out of valid range [-100, 60]")

        # Humidity validation
        humidity = weather.get("humidity")
        if humidity is not None:
            if humidity < 0 or humidity > 100:
                errors.append(f"Humidity {humidity}% out of valid range [0, 100]")

        # Rainfall validation
        rainfall = weather.get("rainfall")
        if rainfall is not None:
            if rainfall < 0:
                errors.append(f"Rainfall {rainfall}mm cannot be negative")
            if rainfall > 500:
                errors.append(f"Rainfall {rainfall}mm exceeds maximum [500mm]")

        # Wind speed validation
        wind_speed = weather.get("wind_speed")
        if wind_speed is not None:
            if wind_speed < 0:
                errors.append(f"Wind speed {wind_speed}m/s cannot be negative")
            if wind_speed > 120:
                errors.append(f"Wind speed {wind_speed}m/s exceeds hurricane force")

        if errors:
            return ValidationResult(False, "; ".join(errors))

        return ValidationResult(True, "Valid weather data")

    @staticmethod
    def validate_sensor_reading(sensor_type: str, value: float) -> ValidationResult:
        """Validate IoT sensor readings against physical limits."""
        if sensor_type not in DataValidator.SENSOR_LIMITS:
            logger.warning(f"Unknown sensor type: {sensor_type}")
            return ValidationResult(True, f"Unknown sensor type, skipping validation")

        limits = DataValidator.SENSOR_LIMITS[sensor_type]

        if value < limits["min"]:
            return ValidationResult(
                False,
                f"{sensor_type} value {value} below minimum {limits['min']} {limits['unit']}"
            )

        if value > limits["max"]:
            return ValidationResult(
                False,
                f"{sensor_type} value {value} exceeds maximum {limits['max']} {limits['unit']}"
            )

        return ValidationResult(True, f"Valid {sensor_type} reading")

    @staticmethod
    def validate_earthquake(data: dict) -> ValidationResult:
        """Validate earthquake data from USGS."""
        if not data:
            return ValidationResult(False, "Empty earthquake data")

        # Check required fields
        required_fields = ["geometry", "properties"]
        for field in required_fields:
            if field not in data:
                return ValidationResult(False, f"Missing required field: {field}")

        # Validate magnitude
        magnitude = data.get("properties", {}).get("mag")
        if magnitude is not None:
            if magnitude < 0 or magnitude > 9.9:
                return ValidationResult(False, f"Invalid magnitude: {magnitude}")

        # Validate coordinates
        geometry = data.get("geometry", {})
        coordinates = geometry.get("coordinates", [])
        if len(coordinates) >= 2:
            lat = coordinates[1]
            lon = coordinates[0]
            coord_result = DataValidator.validate_coordinates(lat, lon)
            if not coord_result.is_valid:
                return coord_result

        return ValidationResult(True, "Valid earthquake data")

    @staticmethod
    def validate_timestamp(timestamp: datetime, max_age_hours: int = 24) -> ValidationResult:
        """Validate that timestamp is not too old."""
        now = datetime.now()
        age = now - timestamp

        if age < timedelta(0):
            return ValidationResult(False, f"Timestamp {timestamp} is in the future")

        if age > timedelta(hours=max_age_hours):
            return ValidationResult(
                False,
                f"Timestamp {timestamp} is older than {max_age_hours} hours"
            )

        return ValidationResult(True, "Valid timestamp")

    @staticmethod
    def validate_incident_report(data: dict) -> ValidationResult:
        """Validate incident report data."""
        errors = []

        # Required fields
        required = ["title", "description", "lat", "lon", "severity"]
        for field in required:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")

        if errors:
            return ValidationResult(False, "; ".join(errors))

        # Validate coordinates
        coord_result = DataValidator.validate_coordinates(data["lat"], data["lon"])
        if not coord_result.is_valid:
            return coord_result

        # Validate severity
        valid_severities = ["low", "medium", "high", "critical"]
        if data["severity"] not in valid_severities:
            return ValidationResult(
                False,
                f"Invalid severity: {data['severity']}. Must be one of {valid_severities}"
            )

        return ValidationResult(True, "Valid incident report")

    @staticmethod
    def sanitize_user_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input text."""
        if not text:
            return ""

        # Strip whitespace
        text = text.strip()

        # Truncate to max length
        if len(text) > max_length:
            text = text[:max_length]

        # Remove null bytes
        text = text.replace("\x00", "")

        return text

    @classmethod
    def validate_batch_sensors(cls, sensors: list) -> Dict[str, Any]:
        """Validate a batch of sensor readings."""
        results = {
            "valid": [],
            "invalid": [],
            "unknown": []
        }

        for sensor in sensors:
            sensor_type = sensor.get("type")
            value = sensor.get("current_value")

            if sensor_type is None or value is None:
                results["unknown"].append(sensor)
                continue

            result = cls.validate_sensor_reading(sensor_type, value)
            if result.is_valid:
                results["valid"].append(sensor)
            else:
                results["invalid"].append({
                    "sensor": sensor,
                    "reason": result.message
                })

        return results


# Singleton instance
data_validator = DataValidator()
