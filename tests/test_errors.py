"""Tests for error handling utilities."""

import pytest
from utils.errors import (
    validate_coordinates, validate_city_name, validate_trip_params,
    ValidationError, APIError, GeolocationError
)

class TestValidateCoordinates:
    """Test coordinate validation."""

    def test_valid_coordinates(self):
        """Test valid latitude and longitude."""
        assert validate_coordinates(28.7041, 77.1025) is True
        assert validate_coordinates(0, 0) is True
        assert validate_coordinates(-90, -180) is True
        assert validate_coordinates(90, 180) is True

    def test_invalid_latitude(self):
        """Test invalid latitude."""
        with pytest.raises(ValidationError, match="Invalid latitude"):
            validate_coordinates(91, 77.1025)

        with pytest.raises(ValidationError, match="Invalid latitude"):
            validate_coordinates(-91, 77.1025)

    def test_invalid_longitude(self):
        """Test invalid longitude."""
        with pytest.raises(ValidationError, match="Invalid longitude"):
            validate_coordinates(28.7041, 181)

        with pytest.raises(ValidationError, match="Invalid longitude"):
            validate_coordinates(28.7041, -181)

class TestValidateCityName:
    """Test city name validation."""

    def test_valid_city_names(self):
        """Test valid city names."""
        assert validate_city_name("Delhi") == "Delhi"
        assert validate_city_name("  Mumbai  ") == "Mumbai"
        assert validate_city_name("New York") == "New York"

    def test_empty_city_name(self):
        """Test empty city name."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_city_name("")

        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_city_name("   ")

    def test_too_short_city_name(self):
        """Test too short city name."""
        with pytest.raises(ValidationError, match="at least 2 characters"):
            validate_city_name("A")

    def test_obviously_invalid_names(self):
        """Test obviously invalid names."""
        with pytest.raises(ValidationError, match="doesn't appear to be a valid"):
            validate_city_name("asdf")

        with pytest.raises(ValidationError, match="doesn't appear to be a valid"):
            validate_city_name("test")

class TestValidateTripParams:
    """Test trip parameter validation."""

    def test_valid_trip_params(self):
        """Test valid trip parameters."""
        assert validate_trip_params(2, 1, 5, (5000, 15000)) is True

    def test_invalid_travelers(self):
        """Test invalid number of travelers."""
        with pytest.raises(ValidationError, match="travelers"):
            validate_trip_params(0, 1, 5, (5000, 15000))

        with pytest.raises(ValidationError, match="travelers"):
            validate_trip_params(101, 1, 5, (5000, 15000))

    def test_invalid_budget_range(self):
        """Test invalid budget range."""
        with pytest.raises(ValidationError, match="Minimum budget"):
            validate_trip_params(2, 1, 5, (15000, 5000))
