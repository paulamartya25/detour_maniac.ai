"""Error handling and logging utilities."""

import logging
import functools
from typing import Optional, Callable, Any
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base exception for application errors."""
    pass

class APIError(AppError):
    """API-related errors."""
    pass

class ValidationError(AppError):
    """Input validation errors."""
    pass

class GeolocationError(AppError):
    """Geolocation-related errors."""
    pass

def handle_errors(
    error_message: str = "An error occurred",
    show_to_user: bool = True,
    fallback_value: Any = None
):
    """Decorator for error handling with user feedback."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                logger.warning(f"Validation error in {func.__name__}: {e}")
                if show_to_user:
                    st.warning(f"⚠️ {str(e)}")
                return fallback_value
            except APIError as e:
                logger.error(f"API error in {func.__name__}: {e}")
                if show_to_user:
                    st.error(f"❌ {error_message}: {str(e)}")
                return fallback_value
            except Exception as e:
                logger.exception(f"Unexpected error in {func.__name__}")
                if show_to_user:
                    st.error(f"❌ {error_message}. Please try again or contact support.")
                return fallback_value
        return wrapper
    return decorator

def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate latitude and longitude."""
    if not (-90 <= lat <= 90):
        raise ValidationError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
    if not (-180 <= lon <= 180):
        raise ValidationError(f"Invalid longitude: {lon}. Must be between -180 and 180.")
    return True

def validate_city_name(city: str) -> str:
    """Validate and clean city name."""
    if not city or not city.strip():
        raise ValidationError("City name cannot be empty.")

    cleaned = city.strip()

    if len(cleaned) < 2:
        raise ValidationError("City name must be at least 2 characters.")

    if len(cleaned) > 100:
        raise ValidationError("City name is too long.")

    # Check for obviously invalid inputs
    if cleaned.lower() in ['test', 'asdf', 'qwerty', '123']:
        raise ValidationError(f"'{cleaned}' doesn't appear to be a valid city name.")

    return cleaned

def validate_trip_params(travelers: int, rooms: int, nights: int, budget: tuple) -> bool:
    """Validate trip parameters."""
    if travelers < 1 or travelers > 100:
        raise ValidationError("Number of travelers must be between 1 and 100.")

    if rooms < 1 or rooms > 50:
        raise ValidationError("Number of rooms must be between 1 and 50.")

    if nights < 1 or nights > 365:
        raise ValidationError("Trip duration must be between 1 and 365 nights.")

    if budget[0] < 500 or budget[1] > 100000:
        raise ValidationError("Budget range seems unrealistic. Please adjust.")

    if budget[0] >= budget[1]:
        raise ValidationError("Minimum budget must be less than maximum budget.")

    return True
