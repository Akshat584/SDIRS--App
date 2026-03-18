import random
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger("SDIRS_IoT_Sensor")

@dataclass
class IoTSensor:
    id: str
    type: str # 'seismic', 'water_level', 'smoke'
    lat: float
    lon: float
    current_value: float
    unit: str
    last_updated: datetime

class IoTSensorService:
    """
    SDIRS IoT Sensor Fusion (Module 1)
    Simulates real-time MQTT integration for seismic, water, and smoke sensors.
    This provides 'Ground Truth' data for high-precision disaster predictions.
    """
    
    _instance = None
    _sensors: Dict[str, IoTSensor] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IoTSensorService, cls).__new__(cls)
            cls._instance._initialize_mock_sensors()
        return cls._instance

    def _initialize_mock_sensors(self):
        """Seed the cache with some mock IoT sensors across the region."""
        mock_data = [
            ("seismic-01", "seismic", 26.85, 80.95, 0.2, "magnitude"),
            ("water-01", "water_level", 26.86, 80.96, 1.5, "meters"),
            ("smoke-01", "smoke", 26.84, 80.94, 15.0, "ppm"),
        ]
        for sid, stype, lat, lon, val, unit in mock_data:
            self._sensors[sid] = IoTSensor(
                id=sid, type=stype, lat=lat, lon=lon, 
                current_value=val, unit=unit, last_updated=datetime.now()
            )

    async def start_mqtt_simulator(self):
        """
        Simulates an MQTT subscriber listening to 'sdirs/sensors/#'
        Updates the ground-truth data in real-time.
        """
        logger.info("SDIRS: Initializing MQTT Sensor Fusion listener...")
        while True:
            # Simulate random sensor fluctuations via MQTT 'messages'
            sensor_id = random.choice(list(self._sensors.keys()))
            sensor = self._sensors[sensor_id]
            
            if sensor.type == "seismic":
                sensor.current_value = round(random.uniform(0.1, 4.5), 2) # Magnitude
            elif sensor.type == "water_level":
                sensor.current_value = round(random.uniform(0.5, 5.0), 2) # Meters
            elif sensor.type == "smoke":
                sensor.current_value = round(random.uniform(10, 400), 2) # PPM
            
            sensor.last_updated = datetime.now()
            # logger.debug(f"MQTT Update: Sensor {sensor_id} reported {sensor.current_value} {sensor.unit}")
            
            await asyncio.sleep(5) # Simulate messages every 5 seconds

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
