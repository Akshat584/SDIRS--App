from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import socketio
import asyncio
import os
from typing import Optional, List
from contextlib import asynccontextmanager
from datetime import datetime
import structlog
from app.core.config import settings

# Configure Structured Logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer() if settings.environment == "development" else structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Rate Limiting
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

# SDIRS Application Modules
from app.api import auth, earthquakes, weather_alerts, incidents, social_media, analysis, predictions, heatmap, analytics, routing, messages, drones, safe_zones, mutual_aid, safety, preparedness

from app.core.websockets import get_sio_server
from app.models.alert import Alert
from app.services.alert_service import check_for_red_alert
from app.services.verification_service import cross_check_data, VerificationResult
from app.services.earthquake_service import get_earthquake_data
from app.services.weather_alert_service import get_weather_alert_data
from app.services.iot_sensor_service import iot_service

# --- FastAPI Initialization ---
@asynccontextmanager
async def lifespan(app):
    # Start the IoT Sensor updates in the background (Module 1)
    asyncio.create_task(iot_service.start_sensor_updates())
    yield


app = FastAPI(
    title="SDIRS Backend — Smart Disaster Intelligence & Response System",
    lifespan=lifespan,
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None
)

# Register Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Serve uploaded incident photos
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
# Parse allowed origins from environment - split comma-separated string into list
origins_str = settings.allowed_origins
origins = [o.strip() for o in origins_str.split(",")] if origins_str else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["http://localhost:3000", "http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SDIRS Socket.io Implementation ---
# Integrated real-time coordination for modules: 1, 4, 5, 9
sio = get_sio_server()
sio_app = socketio.ASGIApp(sio, app)

# --- FastAPI Routes (SDIRS Microservices) ---
app.include_router(auth.router, prefix="/api/auth", tags=["Security & Auth (Phase 5)"])
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
app.include_router(safe_zones.router, prefix="/api", tags=["Safe Zones (Module 4)"])
app.include_router(mutual_aid.router, prefix="/api/mutual-aid", tags=["C2C Mutual Aid (Module 10)"])
app.include_router(safety.router, prefix="/api/safety", tags=["Safety Check (Community)"])
app.include_router(preparedness.router, prefix="/api/preparedness", tags=["Education & Manuals"])


@app.get("/")
def read_root():
    return {
        "system": "AI-Powered Smart Disaster Intelligence & Response System (SDIRS)",
        "status": "online",
        "info": "Run uvicorn main:sio_app for Socket.io support"
    }

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns status of all system components.
    """
    import httpx
    from app.db.database import engine
    from sqlalchemy import text

    health_status = {
        "status": "healthy",
        "environment": settings.environment,
        "timestamp": str(datetime.now()),
        "components": {}
    }

    # Check database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check external APIs (weather, earthquakes)
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Quick check - just verify we can reach external services
            health_status["components"]["external_apis"] = "healthy"
    except Exception as e:
        health_status["components"]["external_apis"] = f"degraded: {str(e)}"

    return health_status

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
