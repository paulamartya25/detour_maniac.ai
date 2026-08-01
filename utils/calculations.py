"""Calculation utilities module for distance and cost computations.

This module provides mathematical calculations for geographic distance
using the Haversine formula.

Requirements: 6.3, 10.3
"""

import math
from typing import Tuple


def calculate_haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Calculate the great-circle distance between two points on Earth.
    
    Uses the Haversine formula to compute distance in kilometers.
    This is the shortest distance over the earth's surface, giving an
    "as-the-crow-flies" distance between the points.
    
    Args:
        lat1: Latitude of first point in decimal degrees
        lon1: Longitude of first point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        lon2: Longitude of second point in decimal degrees
    
    Returns:
        Distance in kilometers
    
    Example:
        >>> # Distance between New York and London (approximately 5570 km)
        >>> distance = calculate_haversine_distance(40.7128, -74.0060, 51.5074, -0.1278)
        >>> print(f"{distance:.0f} km")
        5570 km
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lon1_rad = math.radians(lon1)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2) ** 2
    a += math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers (mean radius)
    earth_radius_km = 6371.0088
    
    return earth_radius_km * c
