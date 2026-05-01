from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="citizen") # 'admin', 'ops', 'responder', 'citizen'
    status = Column(String(20), default="active") # 'active', 'inactive', 'on_duty'
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Security: Account Lockout
    failed_login_attempts = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    incidents = relationship("Incident", back_populates="reporter")
    messages = relationship("Message", back_populates="sender")
    allocations = relationship("Allocation", back_populates="responder_user")
    location_history = relationship("LocationHistory", back_populates="user")

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    incident_type = Column(String(50), nullable=True) # 'fire', 'flood', etc.
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    photo_url = Column(String(255), nullable=True)
    
    # AI Verification & Intelligence
    ai_verified = Column(Boolean, default=False)
    ai_confidence = Column(Float, nullable=True)
    predicted_severity = Column(String(20), nullable=True) # 'low', 'medium', 'high', 'critical'
    actual_severity = Column(String(20), nullable=True)
    
    status = Column(String(20), default="pending") # 'pending', 'verified', 'dispatched', 'active', 'resolved', 'fake'
    weather_snapshot = Column(JSON, nullable=True)
    
    reported_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    reporter = relationship("User", back_populates="incidents")
    allocations = relationship("Allocation", back_populates="incident")
    messages = relationship("Message", back_populates="incident")
    analytics = relationship("AnalyticsMetric", back_populates="incident")

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False) # 'ambulance', 'fire_truck', 'drone', etc.
    status = Column(String(20), default="available") # 'available', 'busy', 'maintenance', 'deployed'
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    capacity = Column(Integer, default=1)
    team_lead_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Smart Resource AI (V2) Fields
    specialized_skills = Column(JSON, default=list)
    equipment_status = Column(JSON, default=dict)
    current_workload = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    allocations = relationship("Allocation", back_populates="resource")

class Allocation(Base):
    __tablename__ = "allocations"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"))
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"))
    responder_user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Specific responder if applicable
    
    allocated_at = Column(DateTime(timezone=True), server_default=func.now())
    dispatched_at = Column(DateTime(timezone=True), nullable=True)
    arrived_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="assigned") # 'assigned', 'en_route', 'on_site', 'completed'

    incident = relationship("Incident", back_populates="allocations")
    resource = relationship("Resource", back_populates="allocations")
    responder_user = relationship("User", back_populates="allocations")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    sender_name = Column(String(100), nullable=True)
    message_text = Column(Text, nullable=False)
    message_type = Column(String(20), default="chat") # 'chat', 'broadcast', 'command'
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", back_populates="messages")
    sender = relationship("User", back_populates="messages")

class LocationHistory(Base):
    __tablename__ = "location_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="location_history")

class DisasterPrediction(Base):
    __tablename__ = "disaster_predictions"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    disaster_type = Column(String(50), nullable=False)
    probability = Column(Float, nullable=False) # 0.0 to 1.0
    alert_level = Column(String(20)) # 'green', 'yellow', 'orange', 'red'
    data_sources = Column(JSON, nullable=True)
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

class AnalyticsMetric(Base):
    __tablename__ = "analytics_metrics"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=True)
    
    response_time_seconds = Column(Integer, nullable=True)
    resolution_time_seconds = Column(Integer, nullable=True)
    resource_utilization_score = Column(Float, nullable=True)
    
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    incident = relationship("Incident", back_populates="analytics")

class SafeZone(Base):
    __tablename__ = "safe_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SOSAlert(Base):
    __tablename__ = "sos_alerts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(String(20), default="high")
    status = Column(String(20), default="active") # 'active', 'responded', 'resolved'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class MutualAidRequest(Base):
    """
    SDIRS Module 10: Citizen-to-Citizen (C2C) Mutual Aid
    Allows neighbors to share resources like generators, tools, and medical kits.
    """
    __tablename__ = "mutual_aid_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_type = Column(String(50), nullable=False) # 'generator', 'tools', 'medical_kit', 'water'
    description = Column(Text)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(20), default="open") # 'open', 'fulfilled', 'cancelled'
    urgency = Column(String(20), default="medium") # 'low', 'medium', 'high'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    responses = relationship("MutualAidResponse", back_populates="request")

class MutualAidResponse(Base):
    __tablename__ = "mutual_aid_responses"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("mutual_aid_requests.id"))
    provider_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text)
    status = Column(String(20), default="pending") # 'pending', 'accepted', 'completed'
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    request = relationship("MutualAidRequest", back_populates="responses")
    provider = relationship("User")

class SupplyLog(Base):
    """
    SDIRS Module 10: Blockchain for Resource Integrity
    Simulates a transparent ledger for tracking critical supplies distribution.
    Each entry includes a hash of the previous entry to ensure integrity.
    """
    __tablename__ = "supply_ledger"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    destination_incident_id = Column(Integer, ForeignKey("incidents.id"))
    authorized_by = Column(Integer, ForeignKey("users.id"))
    
    # Integrity Fields
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    previous_hash = Column(String(64), nullable=True)
    current_hash = Column(String(64), unique=True)
    
    # Metadata
    metadata_json = Column(JSON, nullable=True) # e.g., {'batch_no': 'A12', 'temp_controlled': true}

    incident = relationship("Incident")
    authorizer = relationship("User")

class SafetyStatus(Base):
    """
    SDIRS Safety Check Feature
    Allows users to mark themselves as safe during a specific incident.
    """
    __tablename__ = "safety_statuses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    status = Column(String(20), default="safe") # 'safe', 'needs_help', 'unknown'
    message = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User")
    incident = relationship("Incident")
