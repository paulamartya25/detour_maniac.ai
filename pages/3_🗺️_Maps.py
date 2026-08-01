"""Maps page with interactive maps and location-based navigation."""

import html
import pandas as pd
import requests
import streamlit as st

from utils.session_state import SessionStateManager
from utils.styling import get_base_styles
from utils.calculations import calculate_haversine_distance

st.set_page_config(page_title="Maps - DETOUR_MANIAX", layout="wide", page_icon="🗺️")
st.markdown(get_base_styles(), unsafe_allow_html=True)

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

@st.cache_data(ttl=604800, show_spinner=False)
def geocode_location(location_name: str) -> dict | None:
    try:
        response = requests.get(
            NOMINATIM_API,
            params={"q": location_name, "format": "jsonv2", "limit": 1},
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

# Retrieve destination from session state
settings = SessionStateManager.get_trip_settings()

if not settings or not settings.destination.strip():
    st.warning("⚠️ Please enter a destination on the homepage first.")
    st.page_link("app.py", label="← Back to Homepage", icon="🏠")
    st.stop()

city = settings.destination

st.markdown(f"# 🗺️ Maps & Navigation for {html.escape(city)}")
st.caption("Interactive map with attraction markers and navigation from your current location")

with st.spinner(f"Loading attractions in {city}..."):
    places = attractions_for(city)

if not places:
    st.info(f"No verified attractions found within {MAX_ATTRACTION_DISTANCE_KM} km of {city}.")
    st.page_link("app.py", label="← Back to Homepage", icon="🏠")
    st.stop()

# Location input section
st.markdown("### 📍 Enter Your Location")
st.caption("Choose how you want to provide your location")

with st.container(border=True):
    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["🔍 Search by City", "📍 Enter Coordinates", "🌐 How to Get GPS Coordinates"])

    with tab1:
        st.markdown("**Search for your current location:**")
        location_name = st.text_input(
            "Your City/Location",
            placeholder="e.g., Mumbai, Delhi, Bangalore, Kolkata",
            key="location_search",
            help="Enter your current city or area"
        )

        if st.button("🔍 Find My Location", type="primary", use_container_width=True):
            if location_name.strip():
                with st.spinner(f"Finding coordinates for {location_name}..."):
                    coords = geocode_location(location_name.strip())
                    if coords:
                        st.session_state["visitor_location"] = coords
                        SessionStateManager.save_user_location(coords["lat"], coords["lon"])
                        st.success(f"✅ Found {location_name}: {coords['lat']:.5f}, {coords['lon']:.5f}")
                        st.rerun()
                    else:
                        st.error(f"❌ Could not find '{location_name}'. Try entering coordinates in the Coordinates tab.")
            else:
                st.warning("Please enter a city name first.")

    with tab2:
        st.markdown("**Enter your GPS coordinates:**")

        col1, col2 = st.columns(2)
        with col1:
            user_lat = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=None,
                format="%.6f",
                help="Example: 28.7041 (for Delhi)",
                key="manual_lat"
            )
        with col2:
            user_lon = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                value=None,
                format="%.6f",
                help="Example: 77.1025 (for Delhi)",
                key="manual_lon"
            )

        if user_lat is not None and user_lon is not None:
            if st.button("✅ Set My Location", type="primary", use_container_width=True):
                location = {"lat": user_lat, "lon": user_lon}
                st.session_state["visitor_location"] = location
                SessionStateManager.save_user_location(user_lat, user_lon)
                st.success(f"✅ Location set: {user_lat:.5f}, {user_lon:.5f}")
                st.rerun()

    with tab3:
        st.markdown("**📱 How to get your GPS coordinates:**")

        st.markdown("""
        **Method 1: Google Maps (Easiest)**
        1. Open [Google Maps](https://www.google.com/maps) on your phone or computer
        2. Right-click (or long-press on mobile) on your location
        3. Click the coordinates that appear at the top
        4. Coordinates are now copied! Paste them in the "Coordinates" tab

        **Method 2: Your Phone's Location**
        - **iPhone:** Settings → Privacy → Location Services → System Services → Compass
        - **Android:** Open Google Maps app → Tap blue dot → See coordinates at top

        **Method 3: Search Your City**
        - Use the "Search by City" tab above
        - Enter your current city name
        - We'll find the coordinates automatically!
        """)

        st.info("💡 **Tip:** The easiest way is to use the 'Search by City' tab and just type your city name!")

    # Show current location if set
    location = st.session_state.get("visitor_location")
    if location:
        st.success(f"📍 **Current location set:** {location['lat']:.5f}, {location['lon']:.5f}")
        if st.button("🗑️ Clear Location", key="clear_loc"):
            st.session_state.pop("visitor_location", None)
            st.rerun()

# Interactive Map
st.markdown("---")
st.markdown(f"### 🗺️ Interactive Map - {html.escape(city)} Attractions")

mappable = [
    place for place in places
    if isinstance(place.get("lat"), (int, float))
    and isinstance(place.get("lon"), (int, float))
]

if mappable:
    coordinate_rows = [
        {
            "place": place["name"],
            "latitude": float(place["lat"]),
            "longitude": float(place["lon"]),
            "color": "#d66745",
            "size": 180,
        }
        for place in mappable
    ]
    map_data = pd.DataFrame(coordinate_rows)

    st.map(
        map_data,
        latitude="latitude",
        longitude="longitude",
        color="color",
        size="size",
        zoom=11,
        use_container_width=True,
    )

    st.markdown("#### 📋 Attraction Coordinates")
    coordinate_table = map_data[["place", "latitude", "longitude"]].copy()
    coordinate_table["latitude"] = coordinate_table["latitude"].round(5)
    coordinate_table["longitude"] = coordinate_table["longitude"].round(5)
    st.dataframe(
        coordinate_table.rename(
            columns={
                "place": "Attraction",
                "latitude": "Latitude",
                "longitude": "Longitude",
            }
        ),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No attractions with valid coordinates to display on the map.")

# Location-based features
st.markdown("---")

location = st.session_state.get("visitor_location")

if not location:
    st.info("ℹ️ **Set your location above** to see distances and get navigation directions to each attraction.")
    st.caption("💡 Tip: Use the 'Search by City' tab for the easiest way to set your location!")
else:
    st.markdown(f"### 🎯 Distances from Your Location")
    st.caption(f"Calculating from: {location['lat']:.5f}, {location['lon']:.5f}")

    st.markdown("---")

    for place in mappable:
        km = calculate_haversine_distance(
            location["lat"], location["lon"],
            place["lat"], place["lon"]
        )

        maps_url = (
            "https://www.google.com/maps/dir/?api=1"
            f"&origin={location['lat']},{location['lon']}"
            f"&destination={place['lat']},{place['lon']}"
            "&travelmode=driving"
        )

        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"#### {html.escape(place['name'])}")
                st.markdown(f"📏 **Distance:** ~{km:.1f} km from your location")
                st.caption(f"📍 Coordinates: {place['lat']:.5f}, {place['lon']:.5f}")
                if place.get("source"):
                    st.markdown(f"[📖 View on Wikipedia]({place['source']})")

            with col2:
                st.link_button(
                    "🧭 Get Directions",
                    maps_url,
                    use_container_width=True,
                    help="Opens in Google Maps"
                )

st.markdown("---")
st.info("💡 Explore **Hotels** and **Attractions** using the sidebar navigation!")
