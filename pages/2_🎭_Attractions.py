"""Attractions page displaying up to 6 verified tourist attractions.

This page shows verified Wikipedia attractions within 45km of the destination
with a clean white background for better readability.

Requirements: 1.1, 1.2, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
"""

import html

import requests
import streamlit as st

from utils.session_state import SessionStateManager
from utils.styling import get_base_styles

# Page configuration
st.set_page_config(page_title="Attractions - DETOUR_MANIAX", layout="wide", page_icon="🎭")

# Apply consistent styling
st.markdown(get_base_styles(), unsafe_allow_html=True)

# Custom styles for Attractions page with white background
st.markdown("""
<style>
.stApp {
    background-color: #ffffff !important;
}
.attraction-header {
    text-align: center;
    margin-bottom: 2rem;
    padding: 2rem 1rem;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
    border-radius: 20px;
}
.attraction-header h1 {
    color: #0b172a;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.5rem;
    margin: 0 0 0.5rem 0;
}
.attraction-header p {
    color: #6b7280;
    font-size: 1.1rem;
}
.attraction-card {
    background: #ffffff;
    border: 2px solid #e5e7eb;
    border-left: 5px solid #667eea;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    margin-bottom: 1.5rem;
    padding: 1.5rem;
    transition: all 0.3s ease;
}
.attraction-card:hover {
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    transform: translateY(-2px);
}
.attraction-eyebrow {
    color: #667eea;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1rem;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}
.attraction-name {
    color: #0b172a;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
}
.attraction-description {
    color: #374151;
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 1rem;
}
.attraction-image {
    border-radius: 12px;
    margin-bottom: 1rem;
    width: 100%;
    max-height: 400px;
    object-fit: cover;
}
.attraction-link {
    color: #667eea;
    font-size: 0.9rem;
    text-decoration: none;
}
.attraction-link:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
NOMINATIM_API = "https://nominatim.openstreetmap.org/search"
MAX_ATTRACTION_DISTANCE_KM = 45

NON_ATTRACTION_CATEGORY_HINTS = (
    "annual event", "recurring event", "book fair", "festival", "conference", "trade fair",
)
ATTRACTION_CATEGORY_HINTS = (
    "tourist attraction", "museum", "gallery", "park", "garden", "zoo",
    "monument", "memorial", "palace", "castle", "church", "cathedral",
    "temple", "mosque", "synagogue", "opera", "theatre", "theater", "tower",
    "bridge", "market", "square", "historic", "heritage", "fort", "fortress",
    "beach", "lake", "waterfall", "forest", "observatory", "aquarium", "amusement",
)

def distance_km(lat1, lon1, lat2, lon2):
    import math
    a = math.sin(math.radians(lat2-lat1)/2)**2
    a += math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
    return 6371.0088 * 2 * math.asin(math.sqrt(a))

@st.cache_data(ttl=604800, show_spinner=False)
def destination_coordinates(city: str) -> dict | None:
    try:
        response = requests.get(
            NOMINATIM_API,
            params={"q": city, "format": "jsonv2", "limit": 1, "featuretype": "city"},
            timeout=10,
            headers={"User-Agent": "detour-maniax/1.0 travel-planner"},
        )
        response.raise_for_status()
        result = response.json()
        if not result:
            return None
        return {"lat": float(result[0]["lat"]), "lon": float(result[0]["lon"])}
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        return None

def is_likely_attraction(page: dict) -> bool:
    category_text = " ".join(
        category.get("title", "").replace("Category:", "").lower()
        for category in page.get("categories", [])
    )
    return (not any(hint in category_text for hint in NON_ATTRACTION_CATEGORY_HINTS) and any(hint in category_text for hint in ATTRACTION_CATEGORY_HINTS))

@st.cache_data(ttl=86400, show_spinner=False)
def attractions_for(city: str) -> list[dict]:
    destination = destination_coordinates(city)
    if not destination:
        return []

    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"tourist attractions in {city}", "gsrnamespace": 0, "gsrlimit": 20,
        "prop": "pageimages|extracts|coordinates|pageprops|categories", "cllimit": "max", "piprop": "thumbnail",
        "pithumbsize": 1800, "exintro": 1, "explaintext": 1, "exsentences": 2,
    }
    try:
        response = requests.get(
            WIKIPEDIA_API,
            params=params,
            timeout=10,
            headers={"User-Agent": "detour-maniax/1.0 travel-planner"},
        )
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {}).values()
    except (requests.RequestException, ValueError):
        return []

    places = []
    requested_name = " ".join(city.lower().split())
    for page in sorted(pages, key=lambda item: int(item.get("index", 9999))):
        if "disambiguation" in page.get("pageprops", {}):
            continue
        name = page.get("title", "").strip()
        description = page.get("extract", "").strip()
        coordinate = page.get("coordinates", [{}])[0]
        if (not name or not description or " ".join(name.lower().split()) == requested_name or not is_likely_attraction(page)):
            continue
        try:
            lat, lon = float(coordinate["lat"]), float(coordinate["lon"])
        except (KeyError, TypeError, ValueError):
            continue

        distance_from_destination = distance_km(destination["lat"], destination["lon"], lat, lon)
        if distance_from_destination > MAX_ATTRACTION_DISTANCE_KM:
            continue

        page_id = page.get("pageid")
        places.append({
            "name": name,
            "description": description,
            "image": page.get("thumbnail", {}).get("source"),
            "lat": lat,
            "lon": lon,
            "source": f"https://en.wikipedia.org/?curid={page_id}" if page_id else None,
            "city_distance": distance_from_destination,
        })

    places.sort(key=lambda item: (item["image"] is None, item["city_distance"]))
    return places[:6]

# Retrieve destination from session state
settings = SessionStateManager.get_trip_settings()

# Check if destination is available
if not settings or not settings.destination.strip():
    st.warning("⚠️ Please enter a destination on the homepage first.")
    st.page_link("app.py", label="← Back to Homepage", icon="🏠")
    st.stop()

city = settings.destination

# Page header
st.markdown(f"""
<div class="attraction-header">
    <h1>🎭 Attractions in {html.escape(city)}</h1>
    <p>Discover verified tourist spots within {MAX_ATTRACTION_DISTANCE_KM} km</p>
</div>
""", unsafe_allow_html=True)

# Fetch attractions
with st.spinner(f"Loading attractions in {city}..."):
    places = attractions_for(city)

if not places:
    st.info(f"No verified attractions found within {MAX_ATTRACTION_DISTANCE_KM} km of {city}.")
    st.page_link("app.py", label="← Back to Homepage", icon="🏠")
    st.stop()

# Display attractions
st.markdown(f"### Featured Attractions ({len(places)} found)")

for idx, place in enumerate(places, 1):
    attraction_name = html.escape(place["name"])
    description = html.escape(place["description"])
    image_url = place.get("image")
    source_url = place.get("source")

    st.markdown(f"""
    <div class="attraction-card">
        <div class="attraction-eyebrow">Attraction {idx} of {len(places)}</div>
        <h2 class="attraction-name">{attraction_name}</h2>
    </div>
    """, unsafe_allow_html=True)

    if image_url:
        st.image(image_url, use_container_width=True)

    st.markdown(f"""
    <div class="attraction-description">
        {description}
    </div>
    """, unsafe_allow_html=True)

    if source_url:
        st.markdown(f'<a href="{source_url}" target="_blank" class="attraction-link">📖 View on Wikipedia →</a>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# Navigation hint
st.markdown("---")
st.info("💡 Explore hotels and maps using the sidebar navigation!")
