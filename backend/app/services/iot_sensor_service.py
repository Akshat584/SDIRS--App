import random
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

from app.services.thingspeak_service import ThingSpeakService, hybrid_iot_service
from app.services.data_validator import DataValidator

logger = logging.getLogger("SDIRS_IoT_Sensor")

@dataclass
class IoTSensor:
    id: str
    type: str  # 'seismic', 'water_level', 'smoke'
    lat: float
    lon: float
    current_value: float
    unit: str
    last_updated: datetime
    data_source: str = "simulation"  # 'thingspeak', 'simulation'

class IoTSensorService:
    """
    SDIRS IoT Sensor Fusion (Module 1)
    Fetches real-time data from ThingSpeak API with simulation fallback.
    Provides 'Ground Truth' data for high-precision disaster predictions.
    """

    _instance = None
    _sensors: Dict[str, IoTSensor] = {}
    _thingspeak_enabled = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IoTSensorService, cls).__new__(cls)
            cls._instance._initialize_sensors()
        return cls._instance

    def _initialize_sensors(self):
        """Initialize sensor cache with default sensors."""
        # Enable ThingSpeak if configured
        from app.core.config import settings
        if settings.thingspeak_channel_id and settings.thingspeak_read_key:
            self.enable_thingspeak(settings.thingspeak_channel_id, settings.thingspeak_read_key)

        # These serve as fallback when ThingSpeak is unavailable
        default_sensors = [
            ("seismic-01", "seismic", 26.85, 80.95, 0.2, "magnitude"),
            ("water-01", "water_level", 26.86, 80.96, 1.5, "meters"),
            ("smoke-01", "smoke", 26.84, 80.94, 15.0, "ppm"),
            ("temp-01", "temperature", 26.87, 80.97, 25.0, "celsius"),
            ("humidity-01", "humidity", 26.83, 80.93, 60.0, "percentage"),
        ]
        for sid, stype, lat, lon, val, unit in default_sensors:
            self._sensors[sid] = IoTSensor(
                id=sid, type=stype, lat=lat, lon=lon,
                current_value=val, unit=unit, last_updated=datetime.now(),
                data_source="simulation"
            )

    def enable_thingspeak(self, channel_id: str, read_key: str):
        """Enable ThingSpeak integration for real sensor data."""
        hybrid_iot_service.enable_thingspeak(channel_id, read_key)
        self._thingspeak_enabled = True
        logger.info(f"SDIRS: ThingSpeak enabled - channel {channel_id}")

    async def _fetch_from_thingspeak(self) -> bool:
        """Fetch latest sensor data from ThingSpeak API."""
        if not self._thingspeak_enabled:
            return False

        try:
            readings = await hybrid_iot_service.get_all_sensors()
            if readings and isinstance(readings, list):
                # Map ThingSpeak readings to local sensors
                type_to_id = {
                    "seismic": "seismic-01",
                    "water_level": "water-01",
                    "smoke": "smoke-01",
                    "temperature": "temp-01",
                    "humidity": "humidity-01"
                }

                for reading in readings:
                    if not isinstance(reading, dict):
                        continue
                    sensor_type = reading.get("type")
                    if sensor_type in type_to_id:
                        sensor_id = type_to_id[sensor_type]
                        value = reading.get("value")

                        # Validate before updating
                        result = DataValidator.validate_sensor_reading(sensor_type, value)
                        if result.is_valid:
                            if sensor_id in self._sensors:
                                self._sensors[sensor_id].current_value = value
                                self._sensors[sensor_id].data_source = "thingspeak"
                                self._sensors[sensor_id].last_updated = datetime.now()

                logger.debug(f"Updated sensors from ThingSpeak: {len(readings)} readings")
                return True
        except Exception as e:
            logger.warning(f"ThingSpeak fetch failed: {e}")

        return False


    def get_all_sensors(self) -> List[IoTSensor]:
        """Returns all current sensor readings."""
        return list(self._sensors.values())

    def update_simulated_sensors(self):
        """Simulates fluctuations for all sensors (useful for testing/demo)."""
        for sensor in self._sensors.values():
            if sensor.type == "seismic":
                sensor.current_value = round(random.uniform(0.1, 4.5), 2)
            elif sensor.type == "water_level":
                sensor.current_value = round(random.uniform(0.5, 5.0), 2)
            elif sensor.type == "smoke":
                sensor.current_value = round(random.uniform(10, 400), 2)
            elif sensor.type == "temperature":
                sensor.current_value = round(random.uniform(15, 40), 1)
            elif sensor.type == "humidity":
                sensor.current_value = round(random.uniform(30, 90), 1)

            sensor.last_updated = datetime.now()
            sensor.data_source = "simulation"

    def update_sensor_value(self, sensor_id: str, value: float):
        """Manually update a sensor's value (useful for testing)."""
        if sensor_id in self._sensors:
            self._sensors[sensor_id].current_value = value
            self._sensors[sensor_id].last_updated = datetime.now()
            self._sensors[sensor_id].data_source = "manual"

    async def start_sensor_updates(self):

        """
        Main update loop: tries ThingSpeak first, falls back to simulation.
        Updates ground-truth data in real-time.
        """
        logger.info("SDIRS: Starting IoT sensor update loop...")
        update_interval = 30 if self._thingspeak_enabled else 5

        while True:
            # Try to fetch from ThingSpeak
            thingspeak_success = await self._fetch_from_thingspeak()

            if not thingspeak_success:
                # Fallback: simulate sensor fluctuations
                sensor_id = random.choice(list(self._sensors.keys()))
                sensor = self._sensors[sensor_id]

                # Generate realistic values based on sensor type
                if sensor.type == "seismic":
                    sensor.current_value = round(random.uniform(0.1, 4.5), 2)
                elif sensor.type == "water_level":
                    sensor.current_value = round(random.uniform(0.5, 5.0), 2)
                elif sensor.type == "smoke":
                    sensor.current_value = round(random.uniform(10, 400), 2)
                elif sensor.type == "temperature":
                    sensor.current_value = round(random.uniform(15, 40), 1)
                elif sensor.type == "humidity":
                    sensor.current_value = round(random.uniform(30, 90), 1)

                sensor.last_updated = datetime.now()
                sensor.data_source = "simulation"

            await asyncio.sleep(update_interval)

    def get_nearby_sensor_data(self, lat: float, lon: float, radius_km: float = 10.0) -> List[IoTSensor]:
        """
        Retrieves ground-truth IoT data near a specific coordinate.
        In real SDIRS, this would be a PostGIS spatial query.
        """
        nearby = []
        for sensor in self._sensors.values():
            # Simple bounding box / distance approximation for simulation
            if abs(sensor.lat - lat) < (radius_km / 111.0) and abs(sensor.lon - lon) < (radius_km / 111.0):
                nearby.append(sensor)
        return nearby

    def get_ground_truth_adjustment(self, lat: float, lon: float) -> Dict[str, float]:
        """
        Calculates how much prediction models should be adjusted based on real-world IoT sensors.
        """
        nearby_sensors = self.get_nearby_sensor_data(lat, lon)
        adjustments = {"flood": 1.0, "fire": 1.0, "seismic": 1.0}
        
        for sensor in nearby_sensors:
            if sensor.type == "water_level" and sensor.current_value > 3.0: # High water
                adjustments["flood"] = 1.5
            if sensor.type == "smoke" and sensor.current_value > 100.0: # Smoke detected
                adjustments["fire"] = 1.8
            if sensor.type == "seismic" and sensor.current_value > 3.0: # Significant tremor
                adjustments["seismic"] = 2.0
                
        return adjustments

# Global singleton
iot_service = IoTSensorService()
