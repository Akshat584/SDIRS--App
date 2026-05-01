import pytest
from app.models.sqlalchemy import AnalyticsMetric, Incident

def test_get_analytics_dashboard(client, auth_headers, db):
    # Seed some data to get > 0 metrics
    incident = Incident(latitude=26.8, longitude=80.9, status="resolved")
    db.add(incident)
    db.commit()
    
    metric = AnalyticsMetric(incident_id=incident.id, response_time_seconds=600, resolution_time_seconds=3600)
    db.add(metric)
    db.commit()

    resp = client.get("/api/dashboard-metrics", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert "performance" in data
    assert "trends" in data
    assert "utilization" in data
    assert "incident_types_distribution" in data

    assert data["performance"]["avg_response_time_minutes"] > 0
    assert data["performance"]["total_incidents_resolved"] >= 1
