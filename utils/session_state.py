"""Session state management module for persistent data across Streamlit pages.

This module provides centralized management of application state that persists
across page navigations, including trip settings, location permissions, and user coordinates.

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Tuple
import streamlit as st


@dataclass
class TripSettings:
    """Immutable trip configuration data.
    
    Attributes:
        destination: City or location name for the trip
        travelers: Number of people traveling (must be > 0)
        rooms: Number of hotel rooms needed (must be > 0)
        check_in: Check-in date for accommodation
        duration_nights: Trip duration in nights (must be > 0)
        price_range: Tuple of (min_price, max_price) per room per night in INR
    """
    destination: str
    travelers: int
    rooms: int
    check_in: date
    duration_nights: int
    price_range: Tuple[int, int]  # (min_price, max_price) per room per night
    
    def is_complete(self) -> bool:
        """Check if all required settings are provided with valid values.
        
        Returns:
            True if all settings are valid and complete, False otherwise
        """
        return bool(
            self.destination.strip() and
            self.travelers > 0 and
            self.rooms > 0 and
            self.duration_nights > 0
        )


class SessionStateManager:
    """Manages persistent state across Streamlit pages.
    
    This class provides static methods to save and retrieve data from Streamlit's
    session state, ensuring data persistence across page navigations.
    """
    
    TRIP_SETTINGS_KEY = "trip_settings"
    LOCATION_PERMISSION_KEY = "location_permission_granted"
    USER_LOCATION_KEY = "user_location"
    
    @staticmethod
    def save_trip_settings(settings: TripSettings) -> None:
        """Store trip settings in session state.
        
        Args:
            settings: TripSettings instance to persist
        """
        st.session_state[SessionStateManager.TRIP_SETTINGS_KEY] = settings
    
    @staticmethod
    def get_trip_settings() -> Optional[TripSettings]:
        """Retrieve trip settings from session state.
        
        Returns:
            TripSettings instance if stored, None otherwise
        """
        return st.session_state.get(SessionStateManager.TRIP_SETTINGS_KEY)
    
    @staticmethod
    def save_location_permission(granted: bool) -> None:
        """Store location permission status.
        
        Args:
            granted: True if user granted location permission, False otherwise
        """
        st.session_state[SessionStateManager.LOCATION_PERMISSION_KEY] = granted
    
    @staticmethod
    def get_location_permission() -> bool:
        """Retrieve location permission status, defaulting to False.
        
        Returns:
            True if permission granted, False otherwise
        """
        return st.session_state.get(SessionStateManager.LOCATION_PERMISSION_KEY, False)
    
    @staticmethod
    def save_user_location(lat: float, lon: float) -> None:
        """Store user's geographic coordinates.
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
        """
        st.session_state[SessionStateManager.USER_LOCATION_KEY] = {"lat": lat, "lon": lon}
    
    @staticmethod
    def get_user_location() -> Optional[dict]:
        """Retrieve user location coordinates.
        
        Returns:
            Dictionary with 'lat' and 'lon' keys if stored, None otherwise
        """
        return st.session_state.get(SessionStateManager.USER_LOCATION_KEY)
