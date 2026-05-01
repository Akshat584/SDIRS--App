from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date, Integer
from datetime import datetime, timedelta
import random

from app.db.database import get_db
from app.models.sqlalchemy import Incident, Resource, AnalyticsMetric, Allocation
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
    
    # 1. Performance Metrics
    avg_response = db.query(func.avg(AnalyticsMetric.response_time_seconds)).scalar() or 0
    avg_resolution = db.query(func.avg(AnalyticsMetric.resolution_time_seconds)).scalar() or 0
    total_resolved = db.query(func.count(Incident.id)).filter(Incident.status == "resolved").scalar() or 0
    
    # AI Accuracy - Mocked for now as we don't have a 'ground truth' comparison in DB yet, 
    # but could be (actual_severity == predicted_severity) / total
    verified_count = db.query(func.count(Incident.id)).filter(Incident.ai_verified == True).scalar() or 1
    accurate_count = db.query(func.count(Incident.id)).filter(
        Incident.ai_verified == True, 
        Incident.actual_severity == Incident.predicted_severity
    ).filter(Incident.actual_severity != None).scalar() or 0
    ai_accuracy = (accurate_count / verified_count * 100) if verified_count > 0 else 95.0

    performance = PerformanceMetrics(
        avg_response_time_minutes=round(avg_response / 60, 1),
        avg_resolution_time_hours=round(avg_resolution / 3600, 1),
        ai_accuracy_percentage=round(ai_accuracy, 1),
        total_incidents_resolved=total_resolved
    )

    # 2. Incident Trends (Last 7 Days)
    trends = []
    seven_days_ago = datetime.now() - timedelta(days=7)
    
    daily_stats = db.query(
        cast(Incident.reported_at, Date).label('date'),
        Incident.predicted_severity,
        func.count(Incident.id).label('count')
    ).filter(Incident.reported_at >= seven_days_ago).group_by('date', Incident.predicted_severity).all()

    for stat in daily_stats:
        # Ensure stat.date is a string or date object before calling strftime
        date_obj = stat.date
        if isinstance(date_obj, str):
             date_str = date_obj # SQLite might return string
        else:
             date_str = date_obj.strftime("%Y-%m-%d")
             
        trends.append(IncidentTrend(
            date=date_str, 
            count=stat.count, 
            severity=stat.predicted_severity or "medium"
        ))
    
    # Fallback for empty trends to ensure dashboard isn't blank during dev
    if not trends:
        today = datetime.now()
        for i in range(7):
            date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            trends.append(IncidentTrend(date=date_str, count=0, severity="medium"))

    # 3. Resource Utilization
    utilization = []
    resource_stats = db.query(
        Resource.resource_type,
        func.count(Resource.id).label('total'),
        func.sum(cast(Resource.status == 'deployed', Integer)).label('active')
    ).group_by(Resource.resource_type).all()

    for stat in resource_stats:
        total = stat.total
        active = stat.active or 0
        percentage = (active / total * 100) if total > 0 else 0
        utilization.append(ResourceUtilization(
            resource_type=stat.resource_type.replace('_', ' ').title(),
            total_units=total,
            active_units=active,
            utilization_percentage=round(percentage, 1)
        ))

    # 4. Incident Type Distribution
    type_counts = db.query(
        Incident.incident_type, 
        func.count(Incident.id)
    ).group_by(Incident.incident_type).all()
    
    incident_types_distribution = {t or "Unknown": c for t, c in type_counts}

    return AnalyticsDashboardResponse(
        performance=performance,
        trends=trends,
        utilization=utilization,
        incident_types_distribution=incident_types_distribution,
        timestamp=datetime.now()
    )
