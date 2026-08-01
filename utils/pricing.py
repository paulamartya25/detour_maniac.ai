"""Hotel pricing model module based on star categories.

This module provides a star-category-based pricing system with well-defined
price ranges per category, along with methods for calculating accommodation
and total trip costs.

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9
"""

from enum import Enum
from typing import Tuple
from dataclasses import dataclass


class HotelStarCategory(Enum):
    """Hotel classification by star rating.
    
    Star categories range from 1-star (budget) to 5-star (luxury).
    """
    ONE_STAR = 1
    TWO_STAR = 2
    THREE_STAR = 3
    FOUR_STAR = 4
    FIVE_STAR = 5


@dataclass(frozen=True)
class PriceRange:
    """Price range in INR per room per night.
    
    Attributes:
        min_price: Minimum price in INR per room per night
        max_price: Maximum price in INR per room per night
    """
    min_price: int
    max_price: int
    
    def midpoint(self) -> int:
        """Calculate the midpoint of the price range.
        
        Returns:
            Integer midpoint value between min and max price
        """
        return (self.min_price + self.max_price) // 2


class HotelPricingModel:
    """Manages hotel pricing based on star categories.
    
    This class defines official price ranges for each star category
    and provides methods to calculate accommodation and total trip costs.
    """
    
    # Official price ranges per star category (INR per room per night)
    # Requirements: 4.3, 4.4, 4.5, 4.6, 4.7
    PRICE_RANGES = {
        HotelStarCategory.ONE_STAR: PriceRange(1000, 2500),
        HotelStarCategory.TWO_STAR: PriceRange(2500, 5000),
        HotelStarCategory.THREE_STAR: PriceRange(5000, 10000),
        HotelStarCategory.FOUR_STAR: PriceRange(10000, 20000),
        HotelStarCategory.FIVE_STAR: PriceRange(20000, 50000),
    }
    
    @staticmethod
    def get_price_range(category: HotelStarCategory) -> PriceRange:
        """Retrieve the price range for a given star category.
        
        Args:
            category: HotelStarCategory enum value
            
        Returns:
            PriceRange for the specified category
        """
        return HotelPricingModel.PRICE_RANGES[category]
    
    @staticmethod
    def calculate_accommodation_cost(
        price_range: Tuple[int, int],
        rooms: int,
        nights: int
    ) -> Tuple[int, int]:
        """Calculate total accommodation cost range.
        
        Args:
            price_range: Tuple of (min_price, max_price) per room per night
            rooms: Number of rooms
            nights: Number of nights
            
        Returns:
            Tuple of (min_total_cost, max_total_cost) in INR
        """
        min_total = price_range[0] * rooms * nights
        max_total = price_range[1] * rooms * nights
        return (min_total, max_total)
    
    @staticmethod
    def estimate_total_trip_cost(
        accommodation_midpoint: int,
        travelers: int,
        duration_nights: int
    ) -> int:
        """Estimate total trip cost including accommodation, food, and transport.
        
        Uses accommodation midpoint plus per-person daily estimates for food (INR 2000)
        and a flat transport buffer (INR 5000).
        
        Args:
            accommodation_midpoint: Midpoint of accommodation cost range
            travelers: Number of travelers
            duration_nights: Trip duration in nights
            
        Returns:
            Estimated total trip cost in INR
        """
        food_cost = travelers * duration_nights * 2000  # INR 2000 per person per day
        transport_cost = 5000  # Flat local transport buffer
        return accommodation_midpoint + food_cost + transport_cost
