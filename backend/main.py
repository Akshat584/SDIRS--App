from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import socketio
import asyncio
import os
from typing import Optional, List

# SDIRS Application Modules
from app.api import earthquakes, weather_alerts, incidents, social_media, analysis, predictions, heatmap, analytics, routing, messages, drones
from app.core.websockets import get_sio_server
from app.models.alert import Alert
from app.services.alert_service import check_for_red_alert
from app.services.verification_service import cross_check_data, VerificationResult
from app.services.earthquake_service import get_earthquake_data
from app.services.weather_alert_service import get_weather_alert_data
from app.services.iot_sensor_service import iot_service

# --- FastAPI Initialization ---
app = FastAPI(title="SDIRS Backend — Smart Disaster Intelligence & Response System")

@app.on_event("startup")
async def startup_event():
    # Start the IoT MQTT Simulator in the background
    asyncio.create_task(iot_service.start_mqtt_simulator())

# Serve uploaded incident photos
os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware for the React Command Center and Expo Mobile App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SDIRS Socket.io Implementation ---
# Integrated real-time coordination for modules: 1, 4, 5, 9
sio = get_sio_server()
sio_app = socketio.ASGIApp(sio, app)

# --- FastAPI Routes (SDIRS Microservices) ---
app.include_router(incidents.router, prefix="/api", tags=["Incidents (Module 2)"])
app.include_router(predictions.router, prefix="/api", tags=["Prediction Engine (Module 1)"])
app.include_router(earthquakes.router, prefix="/api", tags=["Disaster Data (Module 1)"])
app.include_router(weather_alerts.router, prefix="/api", tags=["Disaster Data (Module 1)"])
app.include_router(social_media.router, prefix="/api", tags=["Verification (Module 3)"])
app.include_router(analysis.router, prefix="/api", tags=["AI Intelligence (Module 10)"])
app.include_router(heatmap.router, prefix="/api", tags=["Heatmap & Risk Visualization (Module 8)"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics & Intelligence (Module 10)"])
app.include_router(routing.router, prefix="/api", tags=["Routing (Module 6)"])
app.include_router(messages.router, prefix="/api", tags=["Communication (Module 9)"])
app.include_router(drones.router, prefix="/api/drones", tags=["Drone Monitoring (Module 7)"])

@app.get("/")
def read_root():
    return {
        "system": "AI-Powered Smart Disaster Intelligence & Response System (SDIRS)",
        "status": "online",
        "info": "Run uvicorn main:sio_app for Socket.io support"
    }

@app.get("/api/red-alert", response_model=Optional[Alert])
async def get_red_alert_status(
    earthquake_magnitude: Optional[float] = Query(None, description="Magnitude of earthquake"),
    flood_event_type: Optional[str] = Query(None, description="Type of flood event (e.g., 'Flash Flood Warning')"),
    wildfire_event_type: Optional[str] = Query(None, description="Type of wildfire event (e.g., 'Red Flag Warning')"),
):
    """
    Check if a red alert should be triggered (Module 1: Disaster Prediction).
    """
    alert = await check_for_red_alert(
        earthquake_magnitude=earthquake_magnitude,
        flood_event_type=flood_event_type,
        wildfire_event_type=wildfire_event_type
    )
    return alert

@app.get("/api/verify-data", response_model=List[VerificationResult])
async def verify_data(
    fetch_earthquakes: bool = Query(False, description="Fetch latest earthquake data"),
    fetch_weather_alerts: bool = Query(False, description="Fetch latest weather alerts (requires lat/lon)"),
    lat: Optional[float] = Query(None, description="Latitude for weather alerts"),
    lon: Optional[float] = Query(None, description="Longitude for weather alerts"),
):
    """
    Module 3: AI Incident Verification System cross-checking logic.
    """
    earthquakes_data = []
    if fetch_earthquakes:
        eq_feed = await get_earthquake_data()
        if eq_feed:
            earthquakes_data = eq_feed.features

    weather_alerts_data = []
    if fetch_weather_alerts and lat is not None and lon is not None:
        wa_feed = await get_weather_alert_data(lat, lon)
        if wa_feed and wa_feed.alerts:
            weather_alerts_data = wa_feed.alerts
    
    verification_results = await cross_check_data(
        earthquakes=earthquakes_data,
        weather_alerts=weather_alerts_data,
        tweets=[] 
    )
    return verification_results
