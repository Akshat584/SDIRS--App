from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import random

from app.models.drone import DroneTelemetry, DroneResponse, DroneFeed
from app.services.drone_sar_service import DroneSARService

router = APIRouter()

# In-memory store for simulated drone fleet
DRONE_FLEET = [
    DroneTelemetry(
        drone_id="SDIRS-DRN-01",
        lat=26.8500, lon=80.9500, altitude=120.0, speed=45.0,
        battery_percentage=82, status="searching",
        search_area=[26.8450, 80.9450, 26.8550, 80.9550], # [min_lat, min_lon, max_lat, max_lon]
        last_update=datetime.now()
    ),
    DroneTelemetry(
        drone_id="SDIRS-DRN-02",
        lat=26.8400, lon=80.9400, altitude=150.0, speed=30.0,
        battery_percentage=65, status="en_route",
        last_update=datetime.now()
    ),
    DroneTelemetry(
        drone_id="SDIRS-DRN-03",
        lat=26.8600, lon=80.9600, altitude=0.0, speed=0.0,
        battery_percentage=98, status="idle",
        last_update=datetime.now()
    )
]

@router.get("/fleet", response_model=DroneResponse)
async def get_drone_fleet():
    """
    SDIRS Module 7: Drone Monitoring System - Get live fleet status with SAR simulation.
    """
    for drone in DRONE_FLEET:
        if drone.status == "searching":
            # Simulate Autonomous S-Pattern and Visual Detection (SAR V1)
            DroneSARService.update_sar_telemetry(drone)
        elif drone.status != "idle":
            # Standard simulation for non-SAR drones
            drone.lat += random.uniform(-0.0005, 0.0005)
            drone.lon += random.uniform(-0.0005, 0.0005)
            drone.battery_percentage = max(0, drone.battery_percentage - 1)
            drone.last_update = datetime.now()
            
    return DroneResponse(
        drones=DRONE_FLEET,
        timestamp=datetime.now()
    )

@router.post("/{drone_id}/assign-sar")
async def assign_sar_mission(drone_id: str, min_lat: float, min_lon: float, max_lat: float, max_lon: float):
    """
    Assign a Search & Rescue mission to a drone with a specific search bounding box.
    """
    drone = next((d for d in DRONE_FLEET if d.drone_id == drone_id), None)
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
        
    drone.status = "searching"
    drone.search_area = [min_lat, min_lon, max_lat, max_lon]
    drone.detections = []
    
    return {"status": "success", "message": f"SAR mission assigned to {drone_id}"}

@router.get("/{drone_id}/stream", response_model=DroneFeed)
async def get_drone_stream(drone_id: str):
    """
    Retrieve the live video stream endpoint for a specific drone.
    In a production system, this would return an RTSP or HLS stream URL.
    """
    drone = next((d for d in DRONE_FLEET if d.drone_id == drone_id), None)
    if not drone:
        raise HTTPException(status_code=404, detail="Drone not found")
        
    return DroneFeed(
        drone_id=drone_id,
        stream_url=f"https://sdirs-stream-service.local/v1/live/{drone_id}/hls/playlist.m3u8",
        is_active=drone.status != "idle",
        incident_id=101 # Mocking an active incident link
    )

@router.post("/{drone_id}/telemetry")
async def update_drone_telemetry(drone_id: str, telemetry: DroneTelemetry):
    """
    Endpoint for hardware drones to report their GPS, battery, and status.
    """
    for i, d in enumerate(DRONE_FLEET):
        if d.drone_id == drone_id:
            DRONE_FLEET[i] = telemetry
            return {"status": "success"}
    
    DRONE_FLEET.append(telemetry)
    return {"status": "created"}
