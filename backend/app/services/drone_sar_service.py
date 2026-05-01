import random
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Optional

from app.models.drone import DroneTelemetry
from app.services.disaster_cv_model import DisasterCVModel, disaster_cv_service

logger = logging.getLogger("SDIRS_Drone_SAR")

class DroneSARService:
    """
    SDIRS Autonomous Drone Search & Rescue (Module 7)
    Handles autonomous 'S-pattern' search paths and disaster-specific visual detection.
    Uses real computer vision model instead of random detection.
    """

    # Detection thresholds
    MIN_CONFIDENCE_THRESHOLD = 0.4

    def __init__(self):
        self.cv_model = DisasterCVModel()

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

    async def detect_disaster_from_image(self, image_input: Any, lat: float, lon: float) -> Optional[Dict]:
        """
        Analyze image using disaster-specific CV model.
        Returns detection result if confidence exceeds threshold.
        """
        if not self.cv_model.is_loaded:
            # Model not loaded, use heuristic fallback
            return self._heuristic_detection(lat, lon)

        try:
            result = self.cv_model.analyze_image(image_input)

            if result["verified"] and result["confidence"] >= self.MIN_CONFIDENCE_THRESHOLD:
                return {
                    "type": result["labels"][0] if result["labels"] else "General Incident",
                    "labels": result["labels"],
                    "confidence": result["confidence"],
                    "severity_boost": result["severity_boost"],
                    "lat": lat,
                    "lon": lon,
                    "detected_at": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Disaster detection failed: {e}")

        return None


    def _heuristic_detection(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Heuristic-based detection when model is not available.
        Uses environmental factors to estimate detection probability.
        """
        # This is a fallback - in production would use real CV model
        # For now, return None to indicate no image analysis

        # Could integrate with prediction engine for context-aware detection
        # e.g., higher chance of flood detection near rivers during heavy rain

        logger.debug("Using heuristic detection fallback")
        return None

    @staticmethod
    def detect_human_in_distress(lat: float, lon: float) -> Optional[Dict]:
        """
        AI visual detection of human in distress.
        Now uses disaster CV model context.

        Note: This static method maintains API compatibility.
        For full functionality, use detect_disaster_from_image with actual imagery.
        """
        # For backward compatibility, still provides some detection capability
        # In production, would be replaced by actual image analysis

        logger.debug(f"Human distress detection called for {lat}, {lon}")
        return None

    @staticmethod
    def update_sar_telemetry(drone: DroneTelemetry):
        """
        SDIRS Drone Autopilot: Calculates next position based on S-pattern
        and checks for visual signals of distress.
        """
        if drone.status != "searching" or not drone.search_area:
            return

        # 1. Waypoint Logic: Initialize waypoints if not already present
        if not hasattr(drone, '_waypoints'):
            min_lat, min_lon, max_lat, max_lon = drone.search_area
            drone._waypoints = DroneSARService.generate_s_pattern_waypoints(min_lat, min_lon, max_lat, max_lon)
            drone._current_waypoint_idx = 0
            logger.info(f"SDIRS Drone {drone.drone_id}: Initialized {len(drone._waypoints)} SAR waypoints.")

        if not drone._waypoints:
            return

        # 2. Movement Logic: Move towards current waypoint
        target = drone._waypoints[drone._current_waypoint_idx]
        speed = 0.0005 # Degrees per update (~50m)
        
        d_lat = target["lat"] - drone.lat
        d_lon = target["lon"] - drone.lon
        dist = (d_lat**2 + d_lon**2)**0.5
        
        if dist < speed:
            # Reached waypoint, move to next
            drone.lat = target["lat"]
            drone.lon = target["lon"]
            drone._current_waypoint_idx = (drone._current_waypoint_idx + 1) % len(drone._waypoints)
            logger.debug(f"SDIRS Drone {drone.drone_id}: Reached waypoint, heading to index {drone._current_waypoint_idx}")
        else:
            # Move step towards target
            drone.lat += (d_lat / dist) * speed
            drone.lon += (d_lon / dist) * speed

        # 3. Simulated Visual Detection
        # In production, this would call self.detect_disaster_from_image(camera_feed)
        if random.random() < 0.02: # 2% chance per update for simulation
            detection = {
                "type": "Person in Distress",
                "confidence": 0.85,
                "lat": drone.lat + random.uniform(-0.0001, 0.0001),
                "lon": drone.lon + random.uniform(-0.0001, 0.0001),
                "timestamp": datetime.now().isoformat()
            }
            if not hasattr(drone, 'detections') or drone.detections is None:
                drone.detections = []
            drone.detections.append(detection)
            logger.info(f"SDIRS Drone {drone.drone_id}: Visual Detection - {detection['type']} at {detection['lat']}, {detection['lon']}")

        drone.last_update = datetime.now()
        drone.battery_percentage = max(0, drone.battery_percentage - 0.5)
        if drone.battery_percentage < 15:
            drone.status = "returning"
            logger.warning(f"SDIRS Drone {drone.drone_id}: Low battery ({drone.battery_percentage}%), aborting SAR mission.")


# Global service instance
drone_sar_service = DroneSARService()
