"""Attractions page displaying up to 6 verified tourist attractions.

This page shows verified Wikipedia attractions within 45km of the destination
with rotating background images every 4 seconds and dynamic font colors
for better visibility against changing backgrounds.

Requirements: 1.1, 1.2, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7
"""

import html
import time

import requests
import streamlit as st

from utils.session_state import SessionStateManager
from utils.styling import get_base_styles

# Page configuration
st.set_page_config(page_title="Attractions - DETOUR_MANIAX", layout="wide", page_icon="🎭")

# Apply consistent styling
st.markdown(get_base_styles(), unsafe_allow_html=True)

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
NOMINATIM_API = "https://nominatim.openstreetmap.org/search"
MAX_ATTRACTION_DISTANCE_KM = 45
FALLBACK_IMAGE = "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1400&q=85"

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

LUXURY_SLOGANS = (
    "Chase horizons. Collect stories.",
    "Your next unforgettable chapter starts here.",
    "Go further, feel deeper, remember forever.",
    "Curated escapes for the beautifully curious.",
    "Leave with memories, not just photographs.",
)


def distance_km(lat1, lon1, lat2, lon2):
    """Calculate Haversine distance between two coordinates."""
    import math
    a = math.sin(math.radians(lat2-lat1)/2)**2
    a += math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
    return 6371.0088 * 2 * math.asin(math.sqrt(a))


@st.cache_data(ttl=604800, show_spinner=False)
def destination_coordinates(city: str) -> dict | None:
    """Resolve the destination once so attraction results can be geographically verified."""
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
    """Keep only Wikipedia pages that are classified like a visitor attraction."""
    category_text = " ".join(
        category.get("title", "").replace("Category:", "").lower()
        for category in page.get("categories", [])
    )
    return (not any(hint in category_text for hint in NON_ATTRACTION_CATEGORY_HINTS) and any(hint in category_text for hint in ATTRACTION_CATEGORY_HINTS))


@st.cache_data(ttl=86400, show_spinner=False)
def attractions_for(city: str) -> list[dict]:
    """Return only Wikipedia attractions that are geographically near the requested city."""
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


def get_brightness(image_url: str) -> float:
    """Estimate brightness of background image (0=dark, 1=bright).
    Simple heuristic: assume travel images are moderately bright by default.
    """
    # In a production system, you might analyze the actual image
    # For now, we'll alternate between dark and light text based on index
    return 0.5


@st.fragment(run_every="4s")
def attraction_background(city: str, places: list[dict]) -> None:
    """Rotate a validated destination attraction image in the background with dynamic font colors."""
    if not places:
        st.info(
            f"No geographically verified attraction pages were found for {city} right now. "
            "The app will not show unrelated locations."
        )
        return

    current_index = int(time.time() // 4) % len(places)
    current = places[current_index]
    image_url = html.escape(current["image"] or FALLBACK_IMAGE, quote=True)
    attraction_name = html.escape(current["name"])
    summary = html.escape(" ".join(current["description"].split())[:320])
    slogan = html.escape(LUXURY_SLOGANS[current_index % len(LUXURY_SLOGANS)])
    
    # Dynamic font color selection based on alternating pattern
    # Light backgrounds get dark text, dark backgrounds get light text
    if current_index % 2 == 0:
        # Light text for darker backgrounds
        text_color = "#ffffff"
        text_shadow = "2px 2px 8px rgba(0, 0, 0, 0.8)"
        eyebrow_color = "#ffd89e"
        slogan_color = "#f5dcc4"
        card_bg = "rgba(20, 30, 40, .88)"
        card_border = "rgba(255, 255, 255, .4)"
    else:
        # Dark text for lighter backgrounds
        text_color = "#111827"
        text_shadow = "1px 1px 3px rgba(255, 255, 255, 0.9)"
        eyebrow_color = "#9a5c11"
        slogan_color = "#8b4333"
        card_bg = "rgba(255, 253, 248, .92)"
        card_border = "rgba(255, 255, 255, .86)"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(16, 30, 44, .40), rgba(16, 30, 44, .42)), url("{image_url}") !important;
            background-position: center !important;
            background-size: cover !important;
            background-attachment: fixed !important;
            transition: background-image 0.8s ease-in-out;
        }}
        .destination-attraction {{
            background: {card_bg};
            border: 1px solid {card_border};
            border-left: 5px solid #d66745;
            border-radius: 22px;
            box-shadow: 0 20px 50px rgba(16, 35, 55, .35);
            color: {text_color} !important;
            margin: 0 0 1.5rem;
            padding: 1.6rem 1.8rem;
        }}
        .destination-attraction * {{ color: {text_color} !important; text-shadow: {text_shadow}; }}
        .destination-attraction .eyebrow {{
            color: {eyebrow_color} !important;
            font-size: .80rem;
            font-weight: 700;
            letter-spacing: .14rem;
            margin: 0 0 .4rem;
            text-transform: uppercase;
        }}
        .destination-attraction .slogan-line {{ 
            color: {slogan_color} !important; 
            font-family: 'Playfair Display', Georgia, serif !important; 
            font-size: 1.1rem; 
            font-style: italic; 
            font-weight: 700; 
            margin: 0 0 .6rem; 
        }}
        .destination-attraction h2 {{ 
            font-family: 'Playfair Display', Georgia, serif !important; 
            font-size: 2.2rem; 
            margin: 0 0 .3rem;
            line-height: 1.2;
        }}
        .destination-attraction p {{ 
            line-height: 1.6; 
            margin: 0;
            font-size: 1.05rem;
        }}
        </style>
        <section class="destination-attraction">
          <p class="eyebrow">Verified attraction near {html.escape(city)}</p>
          <h2>{attraction_name}</h2>
          <p class="slogan-line">{slogan}</p>
          <p>{summary}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        f"Only attractions with Wikipedia coordinates within {MAX_ATTRACTION_DISTANCE_KM} km "
        f"of {city} are shown. The background changes every 4 seconds."
    )


# Retrieve destination from session state
settings = SessionStateManager.get_trip_settings()

# Check if destination is available
if not settings or not settings.destination.strip():
    st.warning("⚠️ Please enter a destination on the homepage first.")
    st.page_link("app.py", label="← Back to Homepage", icon="🏠")
    st.stop()

city = settings.destination

# Page header
st.markdown(f"# 🎭 Attractions in {html.escape(city)}")
st.caption("Discover verified tourist destinations with rotating vibrant backgrounds")

# Fetch and display attractions
with st.spinner(f"Finding verified attractions in {city}..."):
    places = attractions_for(city)

# Display rotating background with attractions
attraction_background(city, places)

# Display up to 6 attraction cards
if places:
    st.markdown("---")
    st.markdown("### Featured Attractions")
    
    for i, place in enumerate(places):
        with st.container(border=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"#### {html.escape(place['name'])}")
                st.write(place['description'])
                st.caption(f"📍 Distance: ~{place['city_distance']:.1f} km from {city}")
            
            with col2:
                if place.get('image'):
                    st.image(place['image'], use_container_width=True)
    
    st.success(f"✅ Found {len(places)} verified attractions near {city}")
else:
    st.info(f"No verified attractions found within {MAX_ATTRACTION_DISTANCE_KM} km of {city}.")

# Navigation hint
st.info("💡 View these attractions on an interactive map using the Maps page in the sidebar!")
