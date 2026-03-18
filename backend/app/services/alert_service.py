from app.services.severity_service import Severity, get_overall_severity
from app.models.alert import Alert
import datetime

async def check_for_red_alert(
    earthquake_magnitude: float = None,
    flood_event_type: str = None,
    wildfire_event_type: str = None
) -> Alert:
    """
    Checks if a red alert should be triggered based on disaster severity.
    """
    overall_severity = get_overall_severity(
        earthquake_magnitude=earthquake_magnitude,
        flood_event_type=flood_event_type,
        wildfire_event_type=wildfire_event_type
    )

    if overall_severity == Severity.CRITICAL:
        return Alert(
            id=1, # Placeholder ID
            message="RED ALERT! Critical disaster event detected.",
            severity=overall_severity.value,
            created_at=datetime.datetime.now()
        )
    return None
