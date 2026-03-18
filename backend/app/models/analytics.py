from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class IncidentTrend(BaseModel):
    date: str
    count: int
    severity: str

class ResourceUtilization(BaseModel):
    resource_type: str
    total_units: int
    active_units: int
    utilization_percentage: float

class PerformanceMetrics(BaseModel):
    avg_response_time_minutes: float
    avg_resolution_time_hours: float
    ai_accuracy_percentage: float
    total_incidents_resolved: int

class AnalyticsDashboardResponse(BaseModel):
    performance: PerformanceMetrics
    trends: List[IncidentTrend]
    utilization: List[ResourceUtilization]
    incident_types_distribution: Dict[str, int]
    timestamp: datetime
