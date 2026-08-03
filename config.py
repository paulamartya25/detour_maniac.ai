"""Configuration and constants for DETOUR_MANIAX application."""

import os
from pathlib import Path

# API Configuration
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
NOMINATIM_API = "https://nominatim.openstreetmap.org/search"

# Business Logic Constants
MAX_ATTRACTION_DISTANCE_KM = 45
ATTRACTION_IMAGE_SIZE = 1800
MAX_ATTRACTIONS_DISPLAY = 6

# Cache TTL (in seconds)
CACHE_TTL_COORDINATES = 604800  # 7 days
CACHE_TTL_ATTRACTIONS = 86400   # 24 hours
CACHE_TTL_GEOCODING = 604800    # 7 days

# User Agent
USER_AGENT = "detour-maniax/1.0 travel-planner"

# Hotel Pricing (INR per room per night)
HOTEL_PRICE_RANGES = {
    1: (1000, 2500),
    2: (2500, 5000),
    3: (5000, 10000),
    4: (10000, 20000),
    5: (20000, 50000),
}

# Trip Cost Estimates
FOOD_COST_PER_PERSON_PER_DAY = 2000  # INR
TRANSPORT_BUFFER = 5000  # INR

# Attraction Category Filters
NON_ATTRACTION_CATEGORIES = (
    "annual event", "recurring event", "book fair",
    "festival", "conference", "trade fair",
)

ATTRACTION_CATEGORIES = (
    "tourist attraction", "museum", "gallery", "park", "garden", "zoo",
    "monument", "memorial", "palace", "castle", "church", "cathedral",
    "temple", "mosque", "synagogue", "opera", "theatre", "theater", "tower",
    "bridge", "market", "square", "historic", "heritage", "fort", "fortress",
    "beach", "lake", "waterfall", "forest", "observatory", "aquarium", "amusement",
)

# UI Configuration
LUXURY_SLOGANS = (
    "Chase horizons. Collect stories.",
    "Your next unforgettable chapter starts here.",
    "Go further, feel deeper, remember forever.",
    "Curated escapes for the beautifully curious.",
    "Leave with memories, not just photographs.",
)

# Paths
BASE_DIR = Path(__file__).parent
COMPONENTS_DIR = BASE_DIR / "components"
