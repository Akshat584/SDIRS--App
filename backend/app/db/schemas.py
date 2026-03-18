from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), server_default="citizen") # 'admin', 'ops', 'responder', 'citizen'
    status = Column(String(20), server_default="active")  # 'active', 'inactive', 'on_duty'
    last_location = Column(Geometry(geometry_type='POINT', srid=4326))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255))
    description = Column(String)
    incident_type = Column(String(50)) # 'fire', 'flood', 'earthquake', 'accident', etc.
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    photo_url = Column(String(255))
    
    # AI Verification & Intelligence
    ai_verified = Column(Boolean, server_default="false")
    ai_confidence = Column(Float)
    predicted_severity = Column(String(20)) # 'low', 'medium', 'high', 'critical'
    actual_severity = Column(String(20))    # confirmed by authorities
    
    status = Column(String(20), server_default="pending") # 'pending', 'verified', 'dispatched', 'active', 'resolved', 'fake'
    weather_snapshot = Column(JSONB) # Store weather conditions at time of report
    
    reported_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    resolved_at = Column(TIMESTAMP(timezone=True))

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False) # 'ambulance', 'fire_truck', 'police_car', 'drone', 'rescue_boat'
    status = Column(String(20), server_default="available") # 'available', 'busy', 'maintenance', 'deployed'
    current_location = Column(Geometry(geometry_type='POINT', srid=4326))
    capacity = Column(Integer, server_default="1")
    team_lead_id = Column(Integer, ForeignKey("users.id"))
    
    # Smart Resource AI (V2) Fields
    specialized_skills = Column(JSONB, server_default='[]') # e.g. ["paramedic", "diver", "firefighter_v2"]
    equipment_status = Column(JSONB, server_default='{}') # e.g. {"fuel": 100, "oxygen": "full"}
    current_workload = Column(Integer, server_default="0") # number of active incidents
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"))
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"))
    allocated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    dispatched_at = Column(TIMESTAMP(timezone=True))
    arrived_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    status = Column(String(20), server_default="assigned") # 'assigned', 'en_route', 'on_site', 'completed'

class DisasterPrediction(Base):
    __tablename__ = "disaster_predictions"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    disaster_type = Column(String(50), nullable=False)
    probability = Column(Float, nullable=False) # 0.0 to 1.0
    alert_level = Column(String(20))    # 'green', 'yellow', 'orange', 'red'
    data_sources = Column(JSONB)         # store references to weather/sensor data used
    predicted_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    expires_at = Column(TIMESTAMP(timezone=True))

class AnalyticsMetric(Base):
    __tablename__ = "analytics_metrics"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    
    response_time_seconds = Column(Integer) # Time from report to arrival
    resolution_time_seconds = Column(Integer) # Time from report to resolved
    resource_utilization_score = Column(Float) # Efficiency score
    
    logged_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    message_text = Column(Text, nullable=False)
    message_type = Column(String(20), server_default="chat") # 'chat', 'broadcast', 'command'
    sent_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
