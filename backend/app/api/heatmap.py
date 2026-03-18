from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
import random

from app.db.database import get_db
from app.db import incidents as db_incidents
from app.models.heatmap import HeatmapPoint, HeatmapResponse
from app.services.prediction_engine import PredictionEngine

router = APIRouter()

@router.get("/heatmap", response_model=HeatmapResponse)
async def get_heatmap_data(
    lat: float = Query(26.8467, description="Center latitude"),
    lon: float = Query(80.9462, description="Center longitude"),
    radius: int = Query(5000, description="Radius in meters"),
    db: Session = Depends(get_db)
):
    """
    SDIRS Module 8: Disaster Heatmap & Risk Visualization.
    Combines live incident reports with AI-predicted risk zones.
    """
    heatmap_points = []
    
    # 1. Fetch Real Incidents from the database
    # In a real app, we'd use a spatial query to get incidents within the radius
    # For now, we'll get all and filter locally for simplicity or just return all
    incidents = db_incidents.get_all_incidents(db)
    
    for inc in incidents:
        # Map severity to intensity
        severity_map = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.5,
            'low': 0.2
        }
        intensity = severity_map.get(inc.predicted_severity.lower(), 0.1) if inc.predicted_severity else 0.3
        
        heatmap_points.append(HeatmapPoint(
            lat=inc.location.lat,
            lon=inc.location.lon,
            intensity=intensity,
            type='incident',
            label=inc.incident_type or "Unknown Incident",
            radius=400
        ))
        
    # 2. Add AI-Predicted Risk Zones
    # We'll generate some simulated risk zones around the center for visualization
    # In a production SDIRS, this would query a pre-calculated risk surface from PG
    
    # Let's use the PredictionEngine to get some mock risks nearby
    for _ in range(3):
        p_lat = lat + random.uniform(-0.02, 0.02)
        p_lon = lon + random.uniform(-0.02, 0.02)
        
        prediction = await PredictionEngine.get_disaster_risks(p_lat, p_lon)
        for risk in prediction.risks:
            if risk.probability > 0.4:  # Only show significant risks on heatmap
                heatmap_points.append(HeatmapPoint(
                    lat=p_lat,
                    lon=p_lon,
                    intensity=risk.probability,
                    type='prediction',
                    label=f"{risk.disaster_type} Risk",
                    radius=800 if risk.alert_level == 'critical' else 600
                ))

    return HeatmapResponse(
        points=heatmap_points,
        timestamp=datetime.now()
    )
