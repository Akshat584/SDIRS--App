from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement
from geoalchemy2 import Geography
import logging
from typing import List, Dict

from app.db import schemas as db_models
from app.models import incident as incident_schemas

logger = logging.getLogger("SDIRS_Resource_AI")

class ResourceAllocationAI:
    """
    SDIRS Smart Resource Allocation AI (Module 5)
    Automatically determines the best team/resource to respond.
    Factors: Distance + Incident Severity + Resource Workload.
    """

    @staticmethod
    def get_nearby_responders(db: Session, incident_location, radius_km: float = 5.0) -> Dict:
        """
        SDIRS Spatial Query (Module 5)
        Finds all responders (users) and ambulances (resources) within a given radius using ST_DWithin.
        Uses PostGIS Geography for accurate meter-based distance calculation.
        """
        radius_meters = radius_km * 1000
        
        # 1. Find nearby Resources (specifically ambulances as requested)
        nearby_resources = db.query(db_models.Resource).filter(
            func.ST_DWithin(
                func.cast(db_models.Resource.current_location, Geography),
                func.cast(incident_location, Geography),
                radius_meters
            ),
            db_models.Resource.resource_type == 'ambulance',
            db_models.Resource.status == 'available'
        ).all()
        
        # 2. Find nearby Responders (Users with responder role)
        nearby_responders = db.query(db_models.User).filter(
            func.ST_DWithin(
                func.cast(db_models.User.last_location, Geography),
                func.cast(incident_location, Geography),
                radius_meters
            ),
            db_models.User.role == 'responder',
            db_models.User.status == 'active'
        ).all()
        
        logger.info(f"SDIRS Spatial Alert: Found {len(nearby_resources)} ambulances and {len(nearby_responders)} responders within {radius_km}km.")
        
        return {
            "resources": nearby_resources,
            "responders": nearby_responders
        }

    @staticmethod
    def suggest_prepositioning(db: Session, risk_data: List) -> List[Dict]:
        """
        SDIRS Predictive Resource Pre-Positioning (Module 5)
        Suggests moving units *before* the disaster hits based on risk levels.
        """
        suggestions = []
        for risk in risk_data:
            if risk.alert_level in ["critical", "high"]:
                # Logic: Suggest moving resources that are currently 'available' and far away
                # to these high-risk zones.
                
                # Determine resource type needed
                needed_type = "ambulance"
                if "Flood" in risk.disaster_type: needed_type = "rescue_boat"
                elif "Wildfire" in risk.disaster_type: needed_type = "fire_truck"
                
                # Mock suggestion logic (in real SDIRS, would search for distant available units)
                suggestions.append({
                    "risk_zone": risk.area,
                    "disaster_type": risk.disaster_type,
                    "recommended_resource": needed_type,
                    "suggested_count": 2 if risk.alert_level == "critical" else 1,
                    "reasoning": f"AI Prediction: {risk.probability*100}% probability of {risk.disaster_type} in {risk.area}."
                })
        
        return suggestions

    @staticmethod
    async def find_best_resources(db: Session, incident_id: int) -> List[int]:
        """
        SDIRS Smart Resource AI (V2)
        Optimizes allocation based on distance, workload, specialized skills, and equipment status.
        """
        # 1. Fetch Incident Details
        incident = db.query(db_models.Incident).filter(db_models.Incident.id == incident_id).first()
        if not incident:
            logger.error(f"Incident {incident_id} not found for allocation.")
            return []

        severity = incident.predicted_severity or "medium"
        incident_type = (incident.incident_type or "general").lower()
        
        # 2. Determine Required Resource Count based on Severity
        required_count = 1
        if severity == "critical": required_count = 5
        elif severity == "high": required_count = 3
        elif severity == "medium": required_count = 2

        # 3. Fetch Candidate Resources (Filter by type if applicable)
        # For simplicity, we filter those who are 'available' or 'deployed' (but not 'busy' or 'maintenance')
        candidates = db.query(db_models.Resource).filter(
            db_models.Resource.status.in_(['available', 'deployed'])
        ).all()

        if not candidates:
            logger.warning(f"No available or deployed resources found for incident {incident_id}.")
            return []

        # 4. Scoring Algorithm (Module 5: V2 Optimization)
        scored_resources = []
        incident_pos = to_shape(incident.location)

        for res in candidates:
            score = 0.0
            
            # A. Distance Scoring (Proximity)
            res_pos = to_shape(res.current_location)
            # Roughly calculate distance in km (using 111km per degree)
            dist_km = ((res_pos.x - incident_pos.x)**2 + (res_pos.y - incident_pos.y)**2)**0.5 * 111
            # Inverse score: 0km = 50 pts, 20km+ = 0 pts
            score += max(0, 50 - (dist_km * 2.5))
            
            # B. Workload Scoring
            # Capacity-aware allocation: higher capacity with lower workload gets more points
            workload_ratio = (res.current_workload or 0) / (res.capacity or 1)
            score += max(0, (1 - workload_ratio) * 30)
            
            # C. Specialized Skills Matching
            skills = res.specialized_skills or []
            # Match keywords based on incident type
            skill_keywords = {
                "flood": ["diver", "boat_pilot", "rescue_swimmer"],
                "fire": ["firefighter", "smoke_jumper"],
                "medical": ["paramedic", "surgeon", "trauma_nurse"],
                "earthquake": ["k9_handler", "structural_eng"]
            }
            
            target_skills = skill_keywords.get(incident_type, [])
            if any(skill in skills for skill in target_skills):
                score += 25
                
            # D. Equipment Status Check
            eq_status = res.equipment_status or {}
            fuel = eq_status.get("fuel", 100)
            if fuel < 20: 
                score -= 40 # Low fuel penalty
            
            # E. Resource Type Affinity
            type_affinity = {
                "fire": ["fire_truck", "drone"],
                "flood": ["rescue_boat", "drone"],
                "earthquake": ["fire_truck", "ambulance"]
            }
            if res.resource_type in type_affinity.get(incident_type, []):
                score += 15

            scored_resources.append((res, score))

        # Sort by score descending
        scored_resources.sort(key=lambda x: x[1], reverse=True)

        # 5. Perform Allocation
        allocated_ids = []
        for resource, score in scored_resources:
            if len(allocated_ids) >= required_count:
                break
            
            # Create Allocation Entry
            new_allocation = db_models.Allocation(
                incident_id=incident_id,
                resource_id=resource.id,
                status='assigned'
            )
            
            # Update Resource Status (V2: Increment workload)
            resource.current_workload = (resource.current_workload or 0) + 1
            if resource.current_workload >= resource.capacity:
                resource.status = 'busy'
            else:
                resource.status = 'deployed'
            
            db.add(new_allocation)
            allocated_ids.append(resource.id)

        db.commit()
        logger.info(f"SDIRS Smart Resource AI (V2) allocated {len(allocated_ids)} resources to incident {incident_id}.")
        return allocated_ids
