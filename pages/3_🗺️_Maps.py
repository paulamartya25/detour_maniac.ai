"""Maps page with AUTOMATIC GPS location fetching."""

import html
import pandas as pd
import requests
import streamlit as st

import streamlit.components.v1 as components
GEOLOCATION_AVAILABLE = True

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
st.markdown("### 📍 Set Your Location")
st.caption("Choose your preferred method to set your location")

with st.container(border=True):
    # Initialize location request state
    if 'location_requested' not in st.session_state:
        st.session_state.location_requested = False

    tab1, tab2, tab3 = st.tabs(["🌍 Get My Location (GPS)", "🔍 Search by City", "📍 Enter Coordinates"])

    with tab1:
        st.markdown("**Automatically fetch your GPS location:**")

        # Use custom HTML/JS component for reliable geolocation
        location_html = """
        <div style="padding: 1rem; background: rgba(255,255,255,0.9); border-radius: 12px;">
            <button id="getLocationBtn" style="
                background: #d66745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                width: 100%;
            ">📍 Get My Location</button>
            <div id="locationResult" style="margin-top: 1rem; font-size: 14px;"></div>
        </div>
        <script>
        const btn = document.getElementById('getLocationBtn');
        const result = document.getElementById('locationResult');

        btn.addEventListener('click', () => {
            if (!navigator.geolocation) {
                result.innerHTML = '❌ Geolocation is not supported by your browser';
                result.style.color = '#d32f2f';
                return;
            }

            btn.disabled = true;
            btn.textContent = '🌍 Getting location...';
            result.innerHTML = '⏳ Requesting your location...';
            result.style.color = '#666';

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude.toFixed(6);
                    const lon = position.coords.longitude.toFixed(6);
                    result.innerHTML = `✅ Location found: ${lat}, ${lon}`;
                    result.style.color = '#2e7d32';
                    btn.textContent = '✅ Location Set';
                    btn.style.background = '#2e7d32';

                    // Send to Streamlit
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: {lat: parseFloat(lat), lon: parseFloat(lon)}
                    }, '*');
                },
                (error) => {
                    let message = '';
                    if (error.code === error.PERMISSION_DENIED) {
                        message = '❌ Location permission denied. Please allow location access in your browser settings.';
                    } else if (error.code === error.POSITION_UNAVAILABLE) {
                        message = '❌ Location information unavailable. Please try again.';
                    } else if (error.code === error.TIMEOUT) {
                        message = '❌ Location request timed out. Please try again.';
                    } else {
                        message = '❌ An unknown error occurred: ' + error.message;
                    }
                    result.innerHTML = message;
                    result.style.color = '#d32f2f';
                    btn.disabled = false;
                    btn.textContent = '📍 Try Again';
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        });
        </script>
        """

        location_data = components.html(location_html, height=150)

        if location_data and isinstance(location_data, dict) and 'lat' in location_data:
            st.session_state["visitor_location"] = location_data
            SessionStateManager.save_user_location(location_data["lat"], location_data["lon"])
            st.success(f"✅ Location set: {location_data['lat']:.6f}, {location_data['lon']:.6f}")
            st.rerun()

        st.caption("⚠️ Your browser will ask for permission. Click 'Allow' to share your location.")

    with tab2:
        st.markdown("**Search for your city:**")

        col1, col2 = st.columns([2, 1])
        with col1:
            location_name = st.text_input(
                "City/Location",
                placeholder="e.g., Mumbai, Delhi, Bangalore",
                key="city_search",
                label_visibility="collapsed"
            )
        with col2:
            search_clicked = st.button("🔍 Find", type="primary", use_container_width=True)

        if search_clicked and location_name.strip():
            with st.spinner(f"Finding {location_name}..."):
                coords = geocode_location(location_name.strip())
                if coords:
                    st.session_state["visitor_location"] = coords
                    SessionStateManager.save_user_location(coords["lat"], coords["lon"])
                    st.success(f"✅ Found: {location_name}")
                    st.rerun()
                else:
                    st.error(f"❌ Could not find '{location_name}'")

    with tab3:
        st.markdown("**Enter coordinates manually:**")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            user_lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=None, format="%.6f", key="lat")
        with col2:
            user_lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=None, format="%.6f", key="lon")
        with col3:
            if user_lat is not None and user_lon is not None:
                if st.button("✅ Set", type="primary", use_container_width=True):
                    location = {"lat": user_lat, "lon": user_lon}
                    st.session_state["visitor_location"] = location
                    SessionStateManager.save_user_location(user_lat, user_lon)
                    st.success("✅ Location set!")
                    st.rerun()

        st.caption("💡 Get coordinates: Right-click on Google Maps → Click coordinates")

    # Show current location status
    location = st.session_state.get("visitor_location")
    if location:
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📍 **Current location:** {location['lat']:.5f}, {location['lon']:.5f}")
        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.session_state.pop("visitor_location", None)
                st.session_state.location_requested = False
                st.rerun()

# Interactive Map
st.markdown("---")
st.markdown(f"### 🗺️ {html.escape(city)} Attractions Map")

mappable = [p for p in places if isinstance(p.get("lat"), (int, float)) and isinstance(p.get("lon"), (int, float))]

if mappable:
    map_data = pd.DataFrame([
        {
            "place": p["name"],
            "latitude": float(p["lat"]),
            "longitude": float(p["lon"]),
            "color": "#d66745",
            "size": 180,
        }
        for p in mappable
    ])

    st.map(map_data, latitude="latitude", longitude="longitude", color="color", size="size", zoom=11, use_container_width=True)

    st.markdown("#### 📋 Attraction Coordinates")
    coord_table = map_data[["place", "latitude", "longitude"]].copy()
    coord_table["latitude"] = coord_table["latitude"].round(5)
    coord_table["longitude"] = coord_table["longitude"].round(5)
    st.dataframe(
        coord_table.rename(columns={"place": "Attraction", "latitude": "Latitude", "longitude": "Longitude"}),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No attractions with valid coordinates to display.")

# Navigation & Directions
st.markdown("---")

location = st.session_state.get("visitor_location")

if not location:
    st.info("ℹ️ Set your location above to see distances and get directions.")
else:
    st.markdown(f"### 🎯 Navigation from Your Location")
    st.caption(f"Calculating from: {location['lat']:.5f}, {location['lon']:.5f}")

    for place in mappable:
        km = calculate_haversine_distance(location["lat"], location["lon"], place["lat"], place["lon"])

        maps_url = (
            f"https://www.google.com/maps/dir/?api=1"
            f"&origin={location['lat']},{location['lon']}"
            f"&destination={place['lat']},{place['lon']}"
            f"&travelmode=driving"
        )

        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"#### {html.escape(place['name'])}")
                st.markdown(f"📏 **{km:.1f} km** from your location")
                st.caption(f"📍 {place['lat']:.5f}, {place['lon']:.5f}")
                if place.get("source"):
                    st.markdown(f"[📖 Wikipedia]({place['source']})")

            with col2:
                st.link_button("🧭 Directions", maps_url, use_container_width=True)

st.markdown("---")
st.info("💡 Explore **Hotels** and **Attractions** using the sidebar!")
