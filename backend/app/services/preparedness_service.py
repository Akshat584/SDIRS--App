from typing import Dict, List, Any

class PreparednessService:
    """
    SDIRS Module 10: Disaster Preparedness & First Aid
    Serves threat-specific manuals and checklists for offline/online use.
    """

    PREPAREDNESS_DATA = {
        "flood": {
            "checklist": [
                "Move to higher ground immediately.",
                "Turn off utilities (gas, electricity) if safe to do so.",
                "Avoid walking or driving through flood waters.",
                "Keep emergency kit ready (Water, Food, Radio, Flashlight)."
            ],
            "first_aid": [
                "Treat any open wounds to prevent infection from contaminated water.",
                "Monitor for hypothermia if exposed to cold water.",
                "Ensure drinking water is boiled or treated."
            ]
        },
        "fire": {
            "checklist": [
                "Evacuate immediately; do not stop to gather belongings.",
                "Stay low to the ground to avoid smoke inhalation.",
                "Check door handles with the back of your hand before opening.",
                "If clothes catch fire: Stop, Drop, and Roll."
            ],
            "first_aid": [
                "Run cool (not cold) water over minor burns for 10-20 minutes.",
                "Do not apply ice, butter, or ointments to serious burns.",
                "Cover burns with a clean, dry cloth."
            ]
        },
        "earthquake": {
            "checklist": [
                "Drop, Cover, and Hold On.",
                "Stay away from windows, mirrors, and hanging objects.",
                "If outdoors, move to a clear area away from buildings and power lines.",
                "Be prepared for aftershocks."
            ],
            "first_aid": [
                "Check for injuries: Head, Neck, and Spine are priorities.",
                "Apply pressure to bleeding wounds.",
                "Immobilize suspected fractures."
            ]
        }
    }

    @staticmethod
    def get_manual(threat_type: str) -> Dict[str, Any]:
        threat = threat_type.lower()
        # Fuzzy match or default
        if "flood" in threat: return PreparednessService.PREPAREDNESS_DATA["flood"]
        if "fire" in threat: return PreparednessService.PREPAREDNESS_DATA["fire"]
        if "earth" in threat: return PreparednessService.PREPAREDNESS_DATA["earthquake"]
        
        return {
            "checklist": ["Stay informed via SDIRS alerts.", "Follow local authority instructions."],
            "first_aid": ["Call emergency services if injuries are severe.", "Keep a basic first aid kit nearby."]
        }
