import math

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on the Earth 
    (specified in decimal degrees) using the Haversine formula.
    
    Returns:
        Distance in kilometers.
    """
    # Earth radius in kilometers
    R = 6371.0
    
    # Convert decimal degrees to radians
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0)**2
    
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return R * c

def is_within_radius(lat1: float, lon1: float, lat2: float, lon2: float, radius_km: float) -> bool:
    """
    Checks if point 2 is within a certain radius of point 1.
    """
    return haversine(lat1, lon1, lat2, lon2) <= radius_km
