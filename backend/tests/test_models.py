import pytest
from app.models.sqlalchemy import User, Incident, Resource, Allocation, Message, SafeZone, SOSAlert
from sqlalchemy.orm import Session

def test_create_user(db: Session):
    user = User(
        name="John Doe",
        email="john@example.com",
        hashed_password="hashed_password",
        role="citizen"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.id is not None
    assert user.name == "John Doe"
    assert user.email == "john@example.com"

def test_create_incident(db: Session, test_user: User):
    incident = Incident(
        reporter_id=test_user.id,
        title="Test Incident",
        description="A test incident",
        latitude=26.8467,
        longitude=80.9462,
        incident_type="fire",
        status="pending"
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    
    assert incident.id is not None
    assert incident.reporter_id == test_user.id
    assert incident.latitude == 26.8467
    assert incident.reporter.name == test_user.name

def test_create_resource(db: Session):
    resource = Resource(
        name="Ambulance 01",
        resource_type="ambulance",
        status="available",
        latitude=26.8467,
        longitude=80.9462,
        capacity=2
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    
    assert resource.id is not None
    assert resource.name == "Ambulance 01"
    assert resource.resource_type == "ambulance"

def test_create_allocation(db: Session, test_user: User):
    # Setup
    incident = Incident(latitude=0, longitude=0)
    resource = Resource(name="R1", resource_type="drone")
    db.add(incident)
    db.add(resource)
    db.commit()
    
    allocation = Allocation(
        incident_id=incident.id,
        resource_id=resource.id,
        responder_user_id=test_user.id,
        status="assigned"
    )
    db.add(allocation)
    db.commit()
    db.refresh(allocation)
    
    assert allocation.id is not None
    assert allocation.incident.id == incident.id
    assert allocation.resource.id == resource.id
    assert allocation.responder_user.id == test_user.id

def test_create_message(db: Session, test_user: User):
    incident = Incident(latitude=0, longitude=0)
    db.add(incident)
    db.commit()
    
    message = Message(
        incident_id=incident.id,
        sender_id=test_user.id,
        sender_name=test_user.name,
        message_text="Help is on the way!",
        message_type="chat"
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    
    assert message.id is not None
    assert message.message_text == "Help is on the way!"
    assert message.sender.id == test_user.id

def test_create_safe_zone(db: Session):
    safe_zone = SafeZone(
        name="Central Shelter",
        latitude=26.85,
        longitude=80.95,
        capacity=500
    )
    db.add(safe_zone)
    db.commit()
    db.refresh(safe_zone)
    
    assert safe_zone.id is not None
    assert safe_zone.name == "Central Shelter"

def test_create_sos_alert(db: Session):
    sos = SOSAlert(
        name="Distress Signal",
        latitude=26.86,
        longitude=80.96,
        severity="critical",
        status="active"
    )
    db.add(sos)
    db.commit()
    db.refresh(sos)
    
    assert sos.id is not None
    assert sos.name == "Distress Signal"
    assert sos.severity == "critical"
