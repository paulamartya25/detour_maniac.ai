"""Tests for pricing utilities."""

import pytest
from utils.pricing import HotelPricingModel, HotelStarCategory, PriceRange

class TestHotelPricingModel:
    """Test suite for hotel pricing calculations."""

    def test_get_price_range_five_star(self):
        """Test 5-star hotel price range."""
        price_range = HotelPricingModel.get_price_range(HotelStarCategory.FIVE_STAR)
        assert price_range.min_price == 20000
        assert price_range.max_price == 50000

    def test_get_price_range_one_star(self):
        """Test 1-star hotel price range."""
        price_range = HotelPricingModel.get_price_range(HotelStarCategory.ONE_STAR)
        assert price_range.min_price == 1000
        assert price_range.max_price == 2500

    def test_calculate_accommodation_cost_single_room(self):
        """Test accommodation cost for single room."""
        budget = (5000, 10000)
        accom_min, accom_max = HotelPricingModel.calculate_accommodation_cost(budget, 1, 3)
        assert accom_min == 15000  # 5000 * 1 * 3
        assert accom_max == 30000  # 10000 * 1 * 3

    def test_calculate_accommodation_cost_multiple_rooms(self):
        """Test accommodation cost for multiple rooms."""
        budget = (10000, 15000)
        accom_min, accom_max = HotelPricingModel.calculate_accommodation_cost(budget, 2, 5)
        assert accom_min == 100000  # 10000 * 2 * 5
        assert accom_max == 150000  # 15000 * 2 * 5

    def test_estimate_total_trip_cost(self):
        """Test total trip cost estimation."""
        accommodation = 50000
        travelers = 2
        nights = 5

        # Expected: 50000 + (2 * 2000 * 5) + 5000 = 50000 + 20000 + 5000 = 75000
        total = HotelPricingModel.estimate_total_trip_cost(accommodation, travelers, nights)
        assert total == 75000

    def test_estimate_total_trip_cost_single_traveler(self):
        """Test cost for single traveler."""
        accommodation = 10000
        travelers = 1
        nights = 3

        # Expected: 10000 + (1 * 2000 * 3) + 5000 = 10000 + 6000 + 5000 = 21000
        total = HotelPricingModel.estimate_total_trip_cost(accommodation, travelers, nights)
        assert total == 21000

class TestPriceRange:
    """Test PriceRange dataclass."""

    def test_price_range_creation(self):
        """Test creating a price range."""
        pr = PriceRange(min_price=1000, max_price=5000)
        assert pr.min_price == 1000
        assert pr.max_price == 5000

    def test_price_range_midpoint(self):
        """Test calculating midpoint."""
        pr = PriceRange(min_price=10000, max_price=20000)
        midpoint = (pr.min_price + pr.max_price) / 2
        assert midpoint == 15000
