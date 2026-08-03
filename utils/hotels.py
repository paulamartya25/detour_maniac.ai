"""Real hotel data fetched from OpenStreetMap via Overpass API."""

import requests
import streamlit as st
from typing import List, Dict, Tuple

# Overpass API endpoint (free, no API key needed)
OVERPASS_API = "https://overpass-api.de/api/interpreter"

def estimate_hotel_stars(tags: dict) -> int:
    """Estimate hotel star rating from OpenStreetMap tags."""
    # Check explicit star rating
    if 'stars' in tags:
        try:
            stars = int(tags['stars'])
            return min(max(stars, 1), 5)  # Clamp between 1-5
        except (ValueError, TypeError):
            pass

    # Estimate based on tourism tag and name
    tourism_type = tags.get('tourism', '').lower()
    name = tags.get('name', '').lower()

    # Luxury indicators
    luxury_keywords = ['taj', 'oberoi', 'itc', 'leela', 'palace', 'grand', 'luxury', 'ritz', 'four seasons', 'shangri']
    if any(keyword in name for keyword in luxury_keywords):
        return 5

    # High-end chains
    upscale_keywords = ['hyatt', 'marriott', 'radisson', 'novotel', 'hilton', 'westin', 'sheraton', 'crowne plaza']
    if any(keyword in name for keyword in upscale_keywords):
        return 4

    # Mid-range
    midrange_keywords = ['lemon tree', 'keys', 'ginger', 'country inn', 'holiday inn express']
    if any(keyword in name for keyword in midrange_keywords):
        return 3

    # Budget
    budget_keywords = ['fab', 'treebo', 'oyo', 'zostel', 'hostel', 'lodge']
    if any(keyword in name for keyword in budget_keywords):
        return 2

    # Default: assume 3-star for hotels, 2-star for guest houses
    if tourism_type == 'guest_house' or 'guest house' in name:
        return 2
    elif tourism_type == 'hotel' or 'hotel' in name:
        return 3

    return 3  # Default

@st.cache_data(ttl=86400, show_spinner=False)  # Cache for 24 hours
def fetch_real_hotels_from_osm(city: str, limit: int = 20) -> List[Dict]:
    """Fetch real hotels from OpenStreetMap for a given city."""
    try:
        # First, get city coordinates
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": city,
            "format": "jsonv2",
            "limit": 1
        }
        headers = {"User-Agent": "detour-maniax/1.0 travel-planner"}

        response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        city_data = response.json()

        if not city_data:
            return []

        lat = float(city_data[0]['lat'])
        lon = float(city_data[0]['lon'])

        # Search radius: 15km around city center
        radius = 15000

        # Overpass query to find hotels
        overpass_query = f"""
        [out:json][timeout:25];
        (
          node["tourism"="hotel"](around:{radius},{lat},{lon});
          way["tourism"="hotel"](around:{radius},{lat},{lon});
          node["tourism"="guest_house"](around:{radius},{lat},{lon});
          way["tourism"="guest_house"](around:{radius},{lat},{lon});
        );
        out body;
        >;
        out skel qt;
        """

        response = requests.post(
            OVERPASS_API,
            data=overpass_query,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        # Parse hotels
        hotels = []
        seen_names = set()

        for element in data.get('elements', []):
            tags = element.get('tags', {})
            name = tags.get('name', '').strip()

            # Skip if no name or already seen
            if not name or name in seen_names:
                continue

            seen_names.add(name)

            # Extract location info
            addr_city = tags.get('addr:city', '')
            addr_area = tags.get('addr:suburb', '') or tags.get('addr:locality', '') or tags.get('addr:neighbourhood', '')

            # Estimate star rating
            stars = estimate_hotel_stars(tags)

            hotels.append({
                'name': name,
                'stars': stars,
                'area': addr_area if addr_area else (addr_city if addr_city else 'City Center'),
                'lat': element.get('lat'),
                'lon': element.get('lon')
            })

            if len(hotels) >= limit:
                break

        # Sort by estimated star rating (high to low)
        hotels.sort(key=lambda h: h['stars'], reverse=True)

        return hotels

    except Exception as e:
        st.warning(f"⚠️ Could not fetch live hotel data: {str(e)}")
        return []

def get_real_hotels(city: str, budget_range: Tuple[int, int]) -> List[Dict]:
    """Get REAL hotels for a city filtered by budget."""
    from utils.pricing import HotelPricingModel, HotelStarCategory

    # Fetch real hotels from OpenStreetMap
    available_hotels = fetch_real_hotels_from_osm(city, limit=30)

    if not available_hotels:
        st.info(f"ℹ️ No real hotel data available for {city}. This could be due to limited OpenStreetMap data or API timeout.")
        return []

    # Filter by budget
    user_min, user_max = budget_range
    filtered = []

    for hotel in available_hotels:
        try:
            star_category = [cat for cat in HotelStarCategory if cat.value == hotel['stars']][0]
            price_range = HotelPricingModel.get_price_range(star_category)

            # Check if hotel price overlaps with user budget
            if price_range.min_price <= user_max and price_range.max_price >= user_min:
                filtered.append({
                    'name': hotel['name'],
                    'category': star_category,
                    'area': hotel['area']
                })
        except (IndexError, KeyError):
            continue

    return filtered
