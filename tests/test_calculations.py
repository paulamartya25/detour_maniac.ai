"""Tests for calculation utilities."""

import pytest
from utils.calculations import calculate_haversine_distance

class TestHaversineDistance:
    """Test suite for distance calculations."""

    def test_distance_same_location(self):
        """Distance between same point should be 0."""
        distance = calculate_haversine_distance(28.7041, 77.1025, 28.7041, 77.1025)
        assert distance == 0.0

    def test_distance_delhi_to_mumbai(self):
        """Test approximate distance Delhi to Mumbai."""
        # Delhi: 28.7041, 77.1025
        # Mumbai: 19.0760, 72.8777
        distance = calculate_haversine_distance(28.7041, 77.1025, 19.0760, 72.8777)
        # Approximate distance is ~1150 km
        assert 1100 < distance < 1200

    def test_distance_bangalore_to_chennai(self):
        """Test approximate distance Bangalore to Chennai."""
        # Bangalore: 12.9716, 77.5946
        # Chennai: 13.0827, 80.2707
        distance = calculate_haversine_distance(12.9716, 77.5946, 13.0827, 80.2707)
        # Approximate distance is ~290 km
        assert 280 < distance < 310

    def test_distance_symmetric(self):
        """Distance should be symmetric (A to B = B to A)."""
        d1 = calculate_haversine_distance(28.7041, 77.1025, 19.0760, 72.8777)
        d2 = calculate_haversine_distance(19.0760, 72.8777, 28.7041, 77.1025)
        assert abs(d1 - d2) < 0.001  # Allow small floating point difference

    def test_distance_non_negative(self):
        """Distance should always be non-negative."""
        distance = calculate_haversine_distance(-33.8688, 151.2093, 48.8566, 2.3522)
        assert distance >= 0
