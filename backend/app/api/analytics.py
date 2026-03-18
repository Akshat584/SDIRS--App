from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import random

from app.db.database import get_db
from app.db import schemas as db_models
from app.models.analytics import AnalyticsDashboardResponse, PerformanceMetrics, IncidentTrend, ResourceUtilization

router = APIRouter()

@router.get("/dashboard-metrics", response_model=AnalyticsDashboardResponse)
async def get_analytics_dashboard(
    db: Session = Depends(get_db)
):
    """
    SDIRS Module 10: AI Intelligence Dashboard & Resource Monitoring.
    Provides high-level performance metrics, resource utilization, and incident trends.
    """
    
    # 1. Performance Metrics (Simulated from database aggregates in production)
    # avg_response_time = db.query(func.avg(db_models.AnalyticsMetric.response_time_seconds)).scalar()
    performance = PerformanceMetrics(
        avg_response_time_minutes=12.5,
        avg_resolution_time_hours=4.2,
        ai_accuracy_percentage=94.8,
        total_incidents_resolved=152
    )

    # 2. Incident Trends (Last 7 Days)
    trends = []
    today = datetime.now()
    for i in range(7):
        date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        trends.append(IncidentTrend(date=date_str, count=random.randint(5, 25), severity="high"))
        trends.append(IncidentTrend(date=date_str, count=random.randint(10, 40), severity="medium"))
    
    # 3. Resource Utilization
    utilization = [
        ResourceUtilization(resource_type="Ambulance", total_units=20, active_units=14, utilization_percentage=70.0),
        ResourceUtilization(resource_type="Fire Truck", total_units=15, active_units=8, utilization_percentage=53.3),
        ResourceUtilization(resource_type="Rescue Drone", total_units=10, active_units=9, utilization_percentage=90.0),
        ResourceUtilization(resource_type="Police Unit", total_units=30, active_units=12, utilization_percentage=40.0)
    ]

    # 4. Incident Type Distribution
    # distribution = db.query(db_models.Incident.incident_type, func.count(db_models.Incident.id)).group_by(db_models.Incident.incident_type).all()
    incident_types_distribution = {
        "Fire": 45,
        "Flood": 32,
        "Medical": 68,
        "Earthquake": 12,
        "Other": 24
    }

    return AnalyticsDashboardResponse(
        performance=performance,
        trends=trends,
        utilization=utilization,
        incident_types_distribution=incident_types_distribution,
        timestamp=datetime.now()
    )
