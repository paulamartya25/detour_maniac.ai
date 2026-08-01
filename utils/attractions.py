"""Attraction verification and filtering module.

This module provides filtering and verification logic for Wikipedia-sourced
tourist attractions, ensuring only geographically verified and relevant
attractions are displayed to users.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class VerifiedAttraction:
    """A tourist attraction verified with Wikipedia coordinates.
    
    Represents an attraction that has passed all filtering criteria:
    - Has valid geographic coordinates
    - Is within maximum distance from destination
    - Matches priority category classifications
    - Does not match excluded categories
    
    Attributes:
        name: The name of the attraction
        description: A brief description of the attraction
        latitude: Geographic latitude in decimal degrees
        longitude: Geographic longitude in decimal degrees
        image_url: Optional URL to an image of the attraction
        source_url: Optional URL to the Wikipedia source page
        distance_from_destination_km: Distance in kilometers from the destination
    """
    name: str
    description: str
    latitude: float
    longitude: float
    image_url: Optional[str]
    source_url: Optional[str]
    distance_from_destination_km: float


class AttractionFilter:
    """Filters and verifies attraction data from Wikipedia.
    
    This class provides static methods for validating and filtering attraction
    data based on geographic proximity, coordinate validity, and category
    classifications. It ensures only relevant tourist attractions are shown
    to users.
    
    Constants:
        MAX_DISTANCE_KM: Maximum allowed distance from destination (45 km)
        EXCLUDED_CATEGORIES: Set of category terms that disqualify an attraction
        PRIORITY_CATEGORIES: Set of category terms that qualify an attraction
    """
    
    MAX_DISTANCE_KM = 45
    
    # Categories to exclude (events, conferences, etc.)
    # Requirement 10.5
    EXCLUDED_CATEGORIES = {
        "annual event",
        "recurring event",
        "book fair",
        "festival",
        "conference",
        "trade fair",
    }
    
    # Priority categories for attractions
    # Requirement 10.6
    PRIORITY_CATEGORIES = {
        "tourist attraction",
        "museum",
        "gallery",
        "park",
        "garden",
        "zoo",
        "monument",
        "memorial",
        "palace",
        "castle",
        "church",
        "cathedral",
        "temple",
        "mosque",
        "synagogue",
        "opera",
        "theatre",
        "theater",  # Include both US and UK spelling
        "tower",
        "bridge",
        "market",
        "square",
        "historic",
        "heritage",
        "fort",
        "fortress",
        "beach",
        "lake",
        "waterfall",
        "forest",
        "observatory",
        "aquarium",
        "amusement",
    }
    
    @staticmethod
    def has_valid_coordinates(attraction_data: dict) -> bool:
        """Check if attraction data contains valid geographic coordinates.
        
        Validates that the attraction has coordinates in the expected format
        and that the latitude and longitude values are within valid ranges.
        
        Args:
            attraction_data: Dictionary containing attraction data with a
                "coordinates" key containing a list of coordinate dictionaries
        
        Returns:
            True if coordinates are present and valid, False otherwise
        
        Validates:
            - Latitude is between -90 and 90 degrees
            - Longitude is between -180 and 180 degrees
        
        Requirement: 10.2
        """
        try:
            coords = attraction_data.get("coordinates", [{}])[0]
            lat, lon = float(coords["lat"]), float(coords["lon"])
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except (KeyError, TypeError, ValueError, IndexError):
            return False
    
    @staticmethod
    def is_within_distance(
        dest_lat: float,
        dest_lon: float,
        attr_lat: float,
        attr_lon: float,
        max_km: float = MAX_DISTANCE_KM
    ) -> bool:
        """Check if attraction is within specified distance from destination.
        
        Uses the Haversine formula to calculate the great-circle distance
        between the destination and the attraction, then checks if it's
        within the maximum allowed distance.
        
        Args:
            dest_lat: Destination latitude in decimal degrees
            dest_lon: Destination longitude in decimal degrees
            attr_lat: Attraction latitude in decimal degrees
            attr_lon: Attraction longitude in decimal degrees
            max_km: Maximum distance in kilometers (default: 45)
        
        Returns:
            True if the attraction is within max_km of the destination,
            False otherwise
        
        Requirements: 10.3, 10.4
        """
        from utils.calculations import calculate_haversine_distance
        distance = calculate_haversine_distance(dest_lat, dest_lon, attr_lat, attr_lon)
        return distance <= max_km
    
    @staticmethod
    def matches_priority_categories(categories: List[str]) -> bool:
        """Check if attraction has priority category classifications.
        
        Analyzes the attraction's Wikipedia categories to determine if it
        matches the priority categories for tourist attractions and does
        not match any excluded categories.
        
        Args:
            categories: List of category strings from Wikipedia
        
        Returns:
            True if the attraction has at least one priority category and
            no excluded categories, False otherwise
        
        Logic:
            - If any excluded category is found, returns False
            - If any priority category is found (and no excluded), returns True
            - Otherwise returns False
        
        Requirements: 10.5, 10.6
        """
        # Normalize categories to lowercase for case-insensitive matching
        category_text = " ".join(cat.lower() for cat in categories)
        
        # Check for excluded categories first
        has_excluded = any(exc in category_text for exc in AttractionFilter.EXCLUDED_CATEGORIES)
        
        # Check for priority categories
        has_priority = any(pri in category_text for pri in AttractionFilter.PRIORITY_CATEGORIES)
        
        # Only return True if has priority categories and no excluded categories
        return not has_excluded and has_priority
    
    @staticmethod
    def filter_and_verify(
        raw_attractions: List[dict],
        destination_lat: float,
        destination_lon: float
    ) -> List[VerifiedAttraction]:
        """Apply all filters and return verified attractions.
        
        Processes a list of raw attraction data from Wikipedia, applying
        all validation and filtering criteria, and returns a list of
        verified attractions sorted by distance from the destination.
        
        Filtering steps:
            1. Validate coordinates are present and in valid ranges
            2. Check category classifications match priority and not excluded
            3. Verify distance is within MAX_DISTANCE_KM
            4. Calculate exact distance for sorting
            5. Sort by distance ascending
            6. Return top 6 attractions
        
        Args:
            raw_attractions: List of dictionaries containing raw attraction data
                from Wikipedia API. Each dict should have:
                - "name": attraction name
                - "description": attraction description
                - "coordinates": list with coordinate dict containing "lat" and "lon"
                - "categories": list of category strings
                - "image": optional image URL
                - "source": optional source URL
            destination_lat: Destination latitude in decimal degrees
            destination_lon: Destination longitude in decimal degrees
        
        Returns:
            List of up to 6 VerifiedAttraction objects sorted by distance
            from destination (closest first)
        
        Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6
        """
        from utils.calculations import calculate_haversine_distance
        
        verified = []
        
        for attr in raw_attractions:
            # Requirement 10.2: Verify coordinates are valid
            if not AttractionFilter.has_valid_coordinates(attr):
                continue
            
            # Requirement 10.5, 10.6: Check category classifications
            if not AttractionFilter.matches_priority_categories(attr.get("categories", [])):
                continue
            
            # Extract coordinates
            coords = attr["coordinates"][0]
            lat, lon = float(coords["lat"]), float(coords["lon"])
            
            # Requirement 10.3, 10.4: Check distance from destination
            if not AttractionFilter.is_within_distance(destination_lat, destination_lon, lat, lon):
                continue
            
            # Calculate exact distance for sorting and storage
            distance = calculate_haversine_distance(destination_lat, destination_lon, lat, lon)
            
            # Create verified attraction object
            verified.append(VerifiedAttraction(
                name=attr.get("name", ""),
                description=attr.get("description", ""),
                latitude=lat,
                longitude=lon,
                image_url=attr.get("image"),
                source_url=attr.get("source"),
                distance_from_destination_km=distance
            ))
        
        # Sort by distance (closest first) and return top 6
        verified.sort(key=lambda a: a.distance_from_destination_km)
        return verified[:6]
