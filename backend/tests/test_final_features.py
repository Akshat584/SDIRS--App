import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.sqlalchemy import User, Incident, Resource
from app.services.blockchain_service import BlockchainSupplyService

def test_mutual_aid_flow(client: TestClient, db: Session):
    # 1. Create a request
    response = client.post(
        "/api/mutual-aid/requests",
        json={
            "item_type": "generator",
            "description": "Need power for medical equipment",
            "latitude": 26.85,
            "longitude": 80.95,
            "urgency": "high"
        }
    )
    assert response.status_code == 200
    req_id = response.json()["id"]

    # 2. List requests
    response = client.get("/api/mutual-aid/requests?item_type=generator")
    assert response.status_code == 200
    assert len(response.json()) >= 1

    # 3. Respond to request
    response = client.post(
        f"/api/mutual-aid/requests/{req_id}/respond",
        params={"message": "I have a spare generator you can use."}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_safety_check_flow(client: TestClient, db: Session, auth_headers):
    # 1. Check in as safe
    response = client.post(
        "/api/safety/check-in",
        json={
            "status": "safe",
            "message": "All good here!",
            "latitude": 26.85,
            "longitude": 80.95
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "safe"

    # 2. Get status using email from test_user
    me_resp = client.get("/api/auth/me", headers=auth_headers)
    email = me_resp.json()["email"]
    
    response = client.get(f"/api/safety/status/{email}")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["message"] == "All good here!"

def test_preparedness_manual(client: TestClient):
    response = client.get("/api/preparedness/manual/flood")
    assert response.status_code == 200
    data = response.json()
    assert "checklist" in data
    assert "first_aid" in data
    assert len(data["checklist"]) > 0

def test_blockchain_supply_integrity(db: Session):
    # 1. Log some distributions
    log1 = BlockchainSupplyService.log_supply_distribution(
        db, "Bottled Water", 100, 1, 1, {"batch": "W1"}
    )
    log2 = BlockchainSupplyService.log_supply_distribution(
        db, "First Aid Kits", 20, 1, 1, {"batch": "F5"}
    )

    assert log2.previous_hash == log1.current_hash
    
    # 2. Verify integrity
    is_valid = BlockchainSupplyService.verify_ledger_integrity(db)
    assert is_valid is True

def test_resource_v2_scoring_logic(db: Session):
    from app.services.resource_allocation_ai import ResourceAllocationAI
    
    # Setup incident
    inc = Incident(latitude=26.85, longitude=80.95, incident_type="fire", predicted_severity="high")
    db.add(inc)
    db.commit()

    # Setup resources with different skills/status
    r1 = Resource(
        name="Fire Pro", resource_type="fire_truck", status="available",
        latitude=26.86, longitude=80.96, specialized_skills=["firefighter"],
        equipment_status={"fuel": 100}, capacity=2, current_workload=0
    )
    r2 = Resource(
        name="Low Fuel Truck", resource_type="fire_truck", status="available",
        latitude=26.85, longitude=80.95, specialized_skills=["firefighter"],
        equipment_status={"fuel": 10}, capacity=2, current_workload=0
    )
    
    db.add_all([r1, r2])
    db.commit()

    # Test allocation
    import asyncio
    allocated_ids = asyncio.run(ResourceAllocationAI.find_best_resources(db, inc.id))
    
    # r1 should be preferred over r2 due to fuel despite being slightly further
    assert r1.id in allocated_ids
    assert r1.current_workload == 1
    assert r1.status == "deployed"
