import random
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from app.models.drone import DroneTelemetry

logger = logging.getLogger("SDIRS_Drone_SAR")

class DroneSARService:
    """
    SDIRS Autonomous Drone Search & Rescue (SAR) (Module 7)
    Handles autonomous 'S-pattern' search paths and visual detection of people in distress.
    """
    
    @staticmethod
    def generate_s_pattern_waypoints(min_lat: float, min_lon: float, max_lat: float, max_lon: float, step_degrees: float = 0.0005) -> List[Dict[str, float]]:
        """
        Generates an S-curve search pattern within a bounding box.
        """
        waypoints = []
        current_lat = min_lat
        moving_east = True
        
        while current_lat <= max_lat:
            if moving_east:
                waypoints.append({"lat": current_lat, "lon": min_lon})
                waypoints.append({"lat": current_lat, "lon": max_lon})
            else:
                waypoints.append({"lat": current_lat, "lon": max_lon})
                waypoints.append({"lat": current_lat, "lon": min_lon})
            
            current_lat += step_degrees
            moving_east = not moving_east
            
        return waypoints

    @staticmethod
    def detect_human_in_distress(lat: float, lon: float) -> Optional[Dict]:
        """
        Simulates AI visual detection of a human waving or in distress from the drone's video feed.
        """
        # 2% chance of finding a human in distress during scanning
        if random.random() < 0.02:
            confidence = 0.85 + (random.random() * 0.14)
            return {
                "type": "human_in_distress",
                "confidence": round(confidence, 2),
                "lat": lat + random.uniform(-0.0001, 0.0001),
                "lon": lon + random.uniform(-0.0001, 0.0001),
                "detected_at": datetime.now().isoformat()
            }
        return None

    @staticmethod
    def update_sar_telemetry(drone: DroneTelemetry):
        """
        SDIRS Drone Autopilot: Calculates the next position based on the S-pattern
        and checks for visual signals of humans in distress.
        """
        if drone.status != "searching" or not drone.search_area:
            return

        min_lat, min_lon, max_lat, max_lon = drone.search_area
        
        # Simple simulated movement in S-pattern
        # In a real SDIRS, the drone would follow precise generated waypoints
        speed_factor = 0.0002
        
        # Simulation logic: drone moves back and forth along LON, slowly increments LAT
        if not hasattr(drone, '_moving_east'):
            drone._moving_east = True

        if drone._moving_east:
            drone.lon += speed_factor
            if drone.lon >= max_lon:
                drone._moving_east = False
                drone.lat += speed_factor # Step up
        else:
            drone.lon -= speed_factor
            if drone.lon <= min_lon:
                drone._moving_east = True
                drone.lat += speed_factor # Step up

        # Reset if we go out of bounds (loop for simulation)
        if drone.lat > max_lat:
            drone.lat = min_lat
            
        # Perform visual AI triage (Module 7: Edge AI on Drone)
        detection = DroneSARService.detect_human_in_distress(drone.lat, drone.lon)
        if detection:
            logger.info(f"SDIRS SAR: {drone.drone_id} DETECTED HUMAN IN DISTRESS at {drone.lat}, {drone.lon}!")
            # In a real scenario, this would trigger a critical incident or update the command center
            if not drone.detections:
                drone.detections = []
            drone.detections.append(detection)
            
        drone.last_update = datetime.now()
        drone.battery_percentage = max(0, drone.battery_percentage - 0.2)
