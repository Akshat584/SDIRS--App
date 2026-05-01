"""
ThingSpeak IoT Integration for SDIRS
Fetches real sensor data from ThingSpeak channels.
"""
import logging
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import httpx

from app.services.data_validator import DataValidator, ValidationResult

logger = logging.getLogger("SDIRS_ThingSpeak")

@dataclass
class ThingSpeakReading:
    """ThingSpeak field reading."""
    field: str
    value: float
    timestamp: datetime

class ThingSpeakService:
    """
    Fetches real IoT sensor data from ThingSpeak API.
    Replaces synthetic sensor data with real measurements.
    """

    def __init__(self, channel_id: str = None, read_key: str = None):
        self.channel_id = channel_id
        self.read_key = read_key
        self.base_url = "https://api.thingspeak.com/channels"
        self._cache: Dict[str, Any] = {}
        self._cache_time: Optional[datetime] = None
        self._cache_ttl_seconds = 60  # Cache for 1 minute

    def _build_url(self, path: str) -> str:
        """Build ThingSpeak API URL."""
        url = f"{self.base_url}/{self.channel_id}/{path}"
        if self.read_key:
            url += f"?api_key={self.read_key}"
        return url

    async def fetch_latest(self) -> Optional[Dict[str, Any]]:
        """Fetch latest readings from ThingSpeak channel."""
        if not self.channel_id:
            logger.warning("ThingSpeak channel ID not configured")
            return None

        try:
            url = self._build_url("feeds/last.json")
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                logger.info(f"ThingSpeak: Fetched latest data from channel {self.channel_id}")
                return data
        except httpx.HTTPError as e:
            logger.error(f"ThingSpeak HTTP error: {e}")
            return None
        except Exception as e:
            logger.error(f"ThingSpeak fetch error: {e}")
            return None

    async def fetch_multiple(self, results: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Fetch multiple recent readings."""
        if not self.channel_id:
            return None

        try:
            url = f"{self.base_url}/{self.channel_id}/feeds.json?results={results}"
            if self.read_key:
                url += f"&api_key={self.read_key}"

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                return data.get("feeds", [])
        except Exception as e:
            logger.error(f"ThingSpeak fetch multiple error: {e}")
            return None

    def map_thingpeak_to_sensors(self, data: Dict[str, Any]) -> List[Dict[str, float]]:
        """
        Map ThingSpeak fields to SDIRS sensor types.

        Field mappings (configurable):
        - field1: seismic (magnitude)
        - field2: water_level (meters)
        - field3: smoke (PPM)
        - field4: temperature (celsius)
        - field5: humidity (percentage)
        """
        if not data:
            return []

        sensors = []

        # Field 1: Seismic
        if data.get("field1"):
            try:
                value = float(data["field1"])
                result = DataValidator.validate_sensor_reading("seismic", value)
                if result.is_valid:
                    sensors.append({
                        "type": "seismic",
                        "value": value,
                        "timestamp": data.get("created_at")
                    })
            except (ValueError, TypeError):
                pass

        # Field 2: Water Level
        if data.get("field2"):
            try:
                value = float(data["field2"])
                result = DataValidator.validate_sensor_reading("water_level", value)
                if result.is_valid:
                    sensors.append({
                        "type": "water_level",
                        "value": value,
                        "timestamp": data.get("created_at")
                    })
            except (ValueError, TypeError):
                pass

        # Field 3: Smoke
        if data.get("field3"):
            try:
                value = float(data["field3"])
                result = DataValidator.validate_sensor_reading("smoke", value)
                if result.is_valid:
                    sensors.append({
                        "type": "smoke",
                        "value": value,
                        "timestamp": data.get("created_at")
                    })
            except (ValueError, TypeError):
                pass

        # Field 4: Temperature
        if data.get("field4"):
            try:
                value = float(data["field4"])
                result = DataValidator.validate_sensor_reading("temperature", value)
                if result.is_valid:
                    sensors.append({
                        "type": "temperature",
                        "value": value,
                        "timestamp": data.get("created_at")
                    })
            except (ValueError, TypeError):
                pass

        # Field 5: Humidity
        if data.get("field5"):
            try:
                value = float(data["field5"])
                result = DataValidator.validate_sensor_reading("humidity", value)
                if result.is_valid:
                    sensors.append({
                        "type": "humidity",
                        "value": value,
                        "timestamp": data.get("created_at")
                    })
            except (ValueError, TypeError):
                pass

        return sensors


class HybridIoTService:
    """
    Hybrid IoT service that tries ThingSpeak first, falls back to simulation.
    This maintains backward compatibility while enabling real data.
    """

    def __init__(self):
        self.thingspeak = None
        self._use_thingspeak = False

    def enable_thingspeak(self, channel_id: str, read_key: str):
        """Enable ThingSpeak integration."""
        self.thingspeak = ThingSpeakService(channel_id, read_key)
        self._use_thingspeak = True
        logger.info(f"ThingSpeak enabled for channel {channel_id}")

    async def get_sensor_reading(self, sensor_type: str) -> Optional[float]:
        """Get latest reading for a specific sensor type."""
        if self._use_thingspeak and self.thingspeak:
            data = await self.thingspeak.fetch_latest()
            if data:
                sensors = self.thingspeak.map_thingpeak_to_sensors(data)
                for sensor in sensors:
                    if sensor["type"] == sensor_type:
                        return sensor["value"]

        # Fallback: return None to indicate no real data
        return None

    async def get_all_sensors(self) -> List[Dict[str, Any]]:
        """Get all sensor readings."""
        if self._use_thingspeak and self.thingspeak:
            data = await self.thingspeak.fetch_latest()
            if data:
                return self.thingspeak.map_thingpeak_to_sensors(data)

        return []


# Global singleton
thingspeak_service = ThingSpeakService()
hybrid_iot_service = HybridIoTService()
