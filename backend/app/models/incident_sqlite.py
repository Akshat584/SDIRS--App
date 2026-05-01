from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    incident_type = Column(String(50), nullable=True)

    # Use lat/lon instead of PostGIS for SQLite
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    photo_url = Column(String(255), nullable=True)

    # AI Verification & Intelligence
    ai_verified = Column(Boolean, default=False)
    ai_confidence = Column(Float, nullable=True)
    predicted_severity = Column(String(20), nullable=True)
    actual_severity = Column(String(20), nullable=True)

    status = Column(String(20), default="pending")
    weather_snapshot = Column(JSON, nullable=True)

    reported_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="citizen")
    status = Column(String(20), default="active")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    status = Column(String(20), default="available")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    capacity = Column(Integer, default=1)
    team_lead_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    specialized_skills = Column(JSON, default=list)
    equipment_status = Column(JSON, default=dict)
    current_workload = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    message_text = Column(Text, nullable=False)
    message_type = Column(String(20), default="chat")
    sent_at = Column(DateTime, default=datetime.utcnow)