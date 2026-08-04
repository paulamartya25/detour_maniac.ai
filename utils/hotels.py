"""Real hotel data fetched from OpenStreetMap via Overpass API."""

import requests
import streamlit as st
from typing import List, Dict, Tuple

OVERPASS_API = "https://overpass-api.de/api/interpreter"

def estimate_hotel_stars(tags: dict) -> int:
    """Estimate hotel star rating from OpenStreetMap tags."""
    if "stars" in tags:
        try:
            stars = int(tags["stars"])
            return min(max(stars, 1), 5)
        except (ValueError, TypeError):
            pass

    name = tags.get("name", "").lower()

    luxury_keywords = ["taj", "oberoi", "itc", "leela", "palace", "grand", "luxury", "ritz", "four seasons", "shangri"]
    if any(keyword in name for keyword in luxury_keywords):
        return 5

    upscale_keywords = ["hyatt", "marriott", "radisson", "novotel", "hilton", "westin", "sheraton", "crowne plaza"]
    if any(keyword in name for keyword in upscale_keywords):
        return 4

    midrange_keywords = ["lemon tree", "keys", "ginger", "country inn", "holiday inn express"]
    if any(keyword in name for keyword in midrange_keywords):
        return 3

    budget_keywords = ["fab", "treebo", "oyo", "zostel", "hostel", "lodge"]
    if any(keyword in name for keyword in budget_keywords):
        return 2

    return 3

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_real_hotels_from_osm(city: str, limit: int = 20) -> List[Dict]:
    """Fetch real hotels from OpenStreetMap for a given city."""
    try:
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        params = {"q": city, "format": "jsonv2", "limit": 1}
        headers = {"User-Agent": "detour-maniax/1.0 travel-planner"}

        response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        city_data = response.json()

        if not city_data:
            return []

        lat = float(city_data[0]["lat"])
        lon = float(city_data[0]["lon"])
        radius = 15000

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

        response = requests.post(OVERPASS_API, data=overpass_query, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        hotels = []
        seen_names = set()

        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name", "").strip()

            if not name or name in seen_names:
                continue

            seen_names.add(name)

            addr_area = tags.get("addr:suburb", "") or tags.get("addr:locality", "") or tags.get("addr:neighbourhood", "") or "City Center"
            stars = estimate_hotel_stars(tags)

            hotels.append({
                "name": name,
                "stars": stars,
                "area": addr_area,
                "lat": element.get("lat"),
                "lon": element.get("lon")
            })

            if len(hotels) >= limit:
                break

        hotels.sort(key=lambda h: h["stars"], reverse=True)
        return hotels

    except Exception as e:
        st.warning(f"Could not fetch live hotel data: {str(e)}")
        return []

def get_real_hotels(city: str, budget_range: Tuple[int, int]) -> List[Dict]:
    """Get REAL hotels for a city filtered by budget."""
    from utils.pricing import HotelPricingModel, HotelStarCategory

    available_hotels = fetch_real_hotels_from_osm(city, limit=30)

    if not available_hotels:
        return []

    user_min, user_max = budget_range
    filtered = []

    for hotel in available_hotels:
        try:
            star_category = [cat for cat in HotelStarCategory if cat.value == hotel["stars"]][0]
            price_range = HotelPricingModel.get_price_range(star_category)

            if price_range.min_price <= user_max and price_range.max_price >= user_min:
                filtered.append({
                    "name": hotel["name"],
                    "category": star_category,
                    "area": hotel["area"]
                })
        except (IndexError, KeyError):
            continue

    return filtered
