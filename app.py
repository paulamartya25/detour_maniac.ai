import html
<<<<<<< HEAD
import math
import time
from datetime import date, timedelta
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

# Import utility modules
from utils.session_state import SessionStateManager, TripSettings
from utils.pricing import HotelPricingModel
from utils.styling import get_base_styles
from utils.calculations import calculate_haversine_distance

st.set_page_config(page_title="DETOUR_MANIAX", layout="wide", page_icon="✈️")

# Apply base styles from styling module
st.markdown(get_base_styles(), unsafe_allow_html=True)

# Additional homepage-specific styles
st.markdown("""
<style>
.block-container { max-width: 1220px; padding-top: 2.4rem; padding-bottom: 3rem; }
.hero { text-align:center; margin: .4rem 0 1.6rem; padding: 1rem 1.25rem; }
.eyebrow { color: #8d5411 !important; font-size: .78rem; font-weight: 700; letter-spacing: .16rem; margin-bottom: .3rem; text-transform: uppercase; }
.title { color: #0b172a !important; font-family: 'Playfair Display', Georgia, serif !important; font-size: clamp(2.7rem, 6vw, 4.8rem); line-height: 1; letter-spacing: -.075rem; margin: 0; }
.tagline { color: #263548 !important; font-family: 'Playfair Display', Georgia, serif !important; font-size: 1.3rem; font-style: italic; font-weight: 600; margin: .65rem 0 0; }
.city-banner, [data-testid="stDataFrame"], [data-testid="stDataFrame"] {
    background: rgba(255, 253, 249, .97) !important; border: 1px solid rgba(255,255,255,.9); border-radius: 20px; box-shadow: 0 16px 42px rgba(23, 45, 68, .18); backdrop-filter: blur(14px);
}
.city-banner { padding: 1rem 1.35rem; margin: 0 0 1rem; }
.city-banner h2 { font-family: 'Playfair Display', Georgia, serif !important; font-size: 2rem; margin: 0; }
[data-testid="stSidebar"] { background: linear-gradient(160deg, rgba(255, 252, 247, .97), rgba(226, 242, 242, .95)); border-right: 1px solid rgba(255,255,255,.72); }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] span,[data-testid="stSidebar"] div { color: #111827 !important; }
[data-testid="stSidebar"] [data-baseweb="input"] { background: rgba(255, 255, 255, .94) !important; border: 1px solid rgba(128, 80, 40, .22) !important; border-radius: 11px !important; }
[data-testid="stSidebar"] [data-baseweb="input"] > div { background: transparent !important; }
[data-testid="stSidebar"] [data-baseweb="input"] input, [data-testid="stSidebar"] [data-baseweb="input"] div { color: #111827 !important; }
[data-testid="stSidebar"] [data-baseweb="slider"] div { color: #111827 !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color: #111827 !important; }
.price-guide { background: linear-gradient(115deg, rgba(255,247,231,.95), rgba(255,255,255,.94)); border: 1px solid rgba(191,130,29,.25); border-radius: 20px; box-shadow: 0 10px 28px rgba(78, 58, 20, .12); margin: 1rem 0; padding: 1.2rem 1.4rem; }
.price-guide h3 { color: #6e4505 !important; margin: 0 0 .35rem; }
.price-guide p { color: #3d3528 !important; margin: 0; }
div[data-testid="stMetric"] { background: rgba(255, 255, 255, .86); border-radius: 16px; padding: .75rem; border: 1px solid rgba(255,255,255,.8); }
div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #111827 !important; }
div[data-testid="stLinkButton"] > a { background: rgba(255, 251, 244, .96) !important; border: 1px solid rgba(181, 91, 61, .38) !important; color: #1c2735 !important; }
div[data-testid="stLinkButton"] > a:hover { background: #f8ddce !important; color: #1c2735 !important; }
</style>
""", unsafe_allow_html=True)

=======
import json
import math
import os
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components
from streamlit.errors import StreamlitSecretNotFoundError
from langchain.agents import create_agent
from langchain_community.callbacks import get_openai_callback
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain_groq import ChatGroq

st.set_page_config(page_title="DETOUR_MANIAX", layout="wide")
get_browser_location = components.declare_component(
    "browser_location", path=str(Path(__file__).parent / "components" / "browser_location")
)
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
ROTATION_MS = 4000
FALLBACK_IMAGE = "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1400&q=85"
>>>>>>> d946654c4c82f35f5ec0762ddfda75b3742d1ee1
LUXURY_SLOGANS = (
    "Chase horizons. Collect stories.",
    "Your next unforgettable chapter starts here.",
    "Go further, feel deeper, remember forever.",
    "Curated escapes for the beautifully curious.",
    "Leave with memories, not just photographs.",
)

<<<<<<< HEAD
# Sidebar with trip settings
=======
def load_groq_api_key() -> str | None:
    """Load a local Streamlit secret, with an environment-variable fallback."""
    try:
        return st.secrets["GROQ_API_KEY"]
    except (KeyError, StreamlitSecretNotFoundError):
        return os.getenv("GROQ_API_KEY")


GROQ_API_KEY = load_groq_api_key()
if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');

:root { --ink: #111827; --muted: #4b5563; --accent: #df5d43; --gold: #bf821d; --surface: rgba(255, 255, 255, .91); }
.stApp {
    background: linear-gradient(115deg, rgba(255, 250, 243, .80), rgba(225, 245, 247, .72)),
        url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1920&q=80") center/cover fixed;
}
.stApp, .stApp p, .stApp label, .stApp span, .stApp [data-testid="stMarkdownContainer"] { font-family: 'DM Sans', Arial, sans-serif; color: var(--ink) !important; }
.stApp h1, .stApp h2, .stApp h3 { color: #101b2d !important; font-family: 'Playfair Display', Georgia, serif !important; font-weight: 700 !important; letter-spacing: -.025em; }
.block-container { max-width: 1220px; padding-top: 2.4rem; padding-bottom: 3rem; }
.hero { text-align:center; margin: .4rem 0 1.6rem; padding: 1rem 1.25rem; }
.eyebrow { color: #8d5411 !important; font-size: .78rem; font-weight: 700; letter-spacing: .16rem; margin-bottom: .3rem; text-transform: uppercase; }
.title { color: #0b172a !important; font-family: 'Playfair Display', Georgia, serif !important; font-size: clamp(2.7rem, 6vw, 4.8rem); line-height: 1; letter-spacing: -.075rem; margin: 0; }
.tagline { color: #263548 !important; font-family: 'Playfair Display', Georgia, serif !important; font-size: 1.3rem; font-style: italic; font-weight: 600; margin: .65rem 0 0; }
.city-banner, .card, [data-testid="stAlert"], [data-testid="stDataFrame"], [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 253, 249, .97) !important; border: 1px solid rgba(255,255,255,.9); border-radius: 20px; box-shadow: 0 16px 42px rgba(23, 45, 68, .18); backdrop-filter: blur(14px);
}
.city-banner { padding: 1rem 1.35rem; margin: 0 0 1rem; }
.city-banner h2 { font-family: 'Playfair Display', Georgia, serif !important; font-size: 2rem; margin: 0; }
.card { padding: 1.8rem; margin-top: 1rem; }
[data-testid="stSidebar"] { background: linear-gradient(160deg, rgba(255, 252, 247, .97), rgba(226, 242, 242, .95)); border-right: 1px solid rgba(255,255,255,.72); }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] span,[data-testid="stSidebar"] div { color: #111827 !important; }
[data-testid="stSidebar"] [data-baseweb="input"] { background: rgba(255, 255, 255, .94) !important; border: 1px solid rgba(128, 80, 40, .22) !important; border-radius: 11px !important; }
[data-testid="stSidebar"] [data-baseweb="input"] > div { background: transparent !important; }
[data-testid="stSidebar"] [data-baseweb="input"] input, [data-testid="stSidebar"] [data-baseweb="input"] div { color: #111827 !important; }
[data-testid="stSidebar"] [data-baseweb="slider"] div { color: #111827 !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] { color: #111827 !important; }
.stButton > button, .stLinkButton > a { background: linear-gradient(135deg, #e4684d, #b7463a) !important; border: 0 !important; border-radius: 12px !important; color: #251510 !important; font-weight: 700 !important; box-shadow: 0 8px 18px rgba(178, 70, 58, .28); transition: transform .18s ease, box-shadow .18s ease; }
.stButton > button:hover, .stLinkButton > a:hover { transform: translateY(-2px); box-shadow: 0 12px 24px rgba(178, 70, 58, .36); color: #251510 !important; }
.price-guide { background: linear-gradient(115deg, rgba(255,247,231,.95), rgba(255,255,255,.94)); border: 1px solid rgba(191,130,29,.25); border-radius: 20px; box-shadow: 0 10px 28px rgba(78, 58, 20, .12); margin: 1rem 0; padding: 1.2rem 1.4rem; }
.price-guide h3 { color: #6e4505 !important; margin: 0 0 .35rem; }
.price-guide p { color: #3d3528 !important; margin: 0; }
div[data-testid="stMetric"] { background: rgba(255, 255, 255, .86); border-radius: 16px; padding: .75rem; border: 1px solid rgba(255,255,255,.8); }
div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #111827 !important; }
div[data-testid="stLinkButton"] > a { background: rgba(255, 251, 244, .96) !important; border: 1px solid rgba(181, 91, 61, .38) !important; color: #1c2735 !important; }
div[data-testid="stLinkButton"] > a:hover { background: #f8ddce !important; color: #1c2735 !important; }
div[data-testid="stDataFrame"], div[data-testid="stTable"] { background: rgba(255, 255, 255, .94) !important; color: #111827 !important; }
div[data-testid="stDataFrame"] *, div[data-testid="stTable"] * { color: #111827 !important; }
</style>
""", unsafe_allow_html=True)


@tool
def search_web(query: str):
    """Search the web for current travel information."""
    return DuckDuckGoSearchRun().run(query)


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
        "pithumbsize": 1400, "exintro": 1, "explaintext": 1, "exsentences": 2,
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

@st.fragment(run_every="4s")
def attraction_background(city: str, places: list[dict]) -> None:
    """Rotate a validated destination attraction image in the background."""
    if not places:
        st.info(
            f"No geographically verified attraction pages were found for {city} right now. "
            "The app will not show unrelated locations."
        )
        return

    current_index = int(time.time() // (ROTATION_MS / 1000)) % len(places)
    current = places[current_index]
    image_url = html.escape(current["image"] or FALLBACK_IMAGE, quote=True)
    attraction_name = html.escape(current["name"])
    summary = html.escape(" ".join(current["description"].split())[:320])
    slogan = html.escape(LUXURY_SLOGANS[current_index % len(LUXURY_SLOGANS)])
    source_url = html.escape(current.get("source") or "", quote=True)
    source_markup = (
        f'<a class="source-link" href="{source_url}" target="_blank" rel="noopener noreferrer">Verified Wikipedia source</a>'
        if source_url else ""
    )

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(16, 30, 44, .44), rgba(16, 30, 44, .48)), url("{image_url}") !important;
            background-position: center !important;
            background-size: cover !important;
            background-attachment: fixed !important;
        }}
        .destination-attraction {{
            background: rgba(255, 253, 248, .94);
            border: 1px solid rgba(255, 255, 255, .86);
            border-left: 5px solid #d66745;
            border-radius: 22px;
            box-shadow: 0 16px 42px rgba(16, 35, 55, .22);
            color: #111827 !important;
            margin: 0 0 1rem;
            padding: 1.35rem 1.6rem;
        }}
        .destination-attraction * {{ color: #111827 !important; }}
        .destination-attraction .eyebrow {{
            color: #9a5c11 !important;
            font-size: .76rem;
            font-weight: 700;
            letter-spacing: .13rem;
            margin: 0 0 .35rem;
            text-transform: uppercase;
        }}
        .destination-attraction .slogan-line {{ color: #8b4333 !important; font-family: Georgia, serif !important; font-size: 1.05rem; font-style: italic; font-weight: 700; margin: 0 0 .55rem; }}
        .destination-attraction h2 {{ font-family: Georgia, serif !important; font-size: 2rem; margin: 0 0 .2rem; }}
        .destination-attraction p {{ line-height: 1.55; margin: 0; }}
        .destination-attraction .source-link {{ color: #75400b !important; display: inline-block; font-size: .86rem; font-weight: 700; margin-top: .8rem; text-decoration: underline; }}
        </style>
        <section class="destination-attraction">
          <p class="eyebrow">Verified attraction near {html.escape(city)}</p>
          <h2>{attraction_name}</h2>
          <p class="slogan-line">{slogan}</p>
          <p>{summary}</p>
          {source_markup}
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.caption(f"Only attractions with Wikipedia coordinates within {MAX_ATTRACTION_DISTANCE_KM} km of {city} are shown. The background changes every 4 seconds.")

def distance_km(lat1, lon1, lat2, lon2):
    a = math.sin(math.radians(lat2-lat1)/2)**2
    a += math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
    return 6371.0088 * 2 * math.asin(math.sqrt(a))


def parse_location(value):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            return None
    if not isinstance(value, dict) or value.get("status") != "success":
        return None
    try:
        lat, lon = float(value["latitude"]), float(value["longitude"])
    except (KeyError, TypeError, ValueError):
        return None
    return {"lat": lat, "lon": lon} if -90 <= lat <= 90 and -180 <= lon <= 180 else None


def guide(places: list[dict], city: str) -> None:
    st.markdown("### Location guide")
    with st.container(border=True):
        browser_value = get_browser_location(
            has_location="visitor_location" in st.session_state,
            key="browser_location_component",
            default=None,
        )
        location = parse_location(browser_value)
        if location:
            st.session_state["visitor_location"] = location
            st.session_state.pop("location_error", None)
        elif isinstance(browser_value, dict) and browser_value.get("status") == "error":
            st.session_state["location_error"] = browser_value.get("message", "Location access was not available.")

        location = st.session_state.get("visitor_location")
        if not location:
            if st.session_state.get("location_error"):
                st.warning(f"Location not shared: {st.session_state['location_error']}")
            st.caption(
                "Share your browser location above to see distances from your current position, "
                "your GPS coordinates, and the verified attraction map."
            )
            return

        mappable = [
            place for place in places
            if isinstance(place.get("lat"), (int, float))
            and isinstance(place.get("lon"), (int, float))
        ]
        if not mappable:
            st.info("Location shared. There are no geographically verified attraction coordinates to map yet.")
            return

        st.success("Location shared. Distances below are from your current position.")
        st.caption(
            f"Your current coordinates: {location['lat']:.5f}, {location['lon']:.5f}. "
            "Distances are direct estimates; Directions opens a route and travel-time estimate."
        )

        coordinate_rows = [
            {
                "place": place["name"],
                "latitude": float(place["lat"]),
                "longitude": float(place["lon"]),
                "color": "#d66745",
                "size": 140,
            }
            for place in mappable
        ]
        map_data = pd.DataFrame(coordinate_rows)

        st.markdown(f"#### Verified {html.escape(city)} attraction map")
        st.map(
            map_data,
            latitude="latitude",
            longitude="longitude",
            color="color",
            size="size",
            zoom=12,
            use_container_width=True,
        )

        coordinate_table = map_data[["place", "latitude", "longitude"]].copy()
        coordinate_table["latitude"] = coordinate_table["latitude"].round(5)
        coordinate_table["longitude"] = coordinate_table["longitude"].round(5)
        st.table(
            coordinate_table.rename(
                columns={
                    "place": "Attraction",
                    "latitude": "Latitude",
                    "longitude": "Longitude",
                }
            )
        )

        for place in mappable:
            km = distance_km(location["lat"], location["lon"], place["lat"], place["lon"])
            maps = (
                "https://www.google.com/maps/dir/?api=1&origin="
                f"{location['lat']},{location['lon']}&destination={place['lat']},{place['lon']}"
            )
            left, right = st.columns([3, 1])
            with left:
                st.markdown(f"**{html.escape(place['name'])}**")
                st.caption(f"About {km:.1f} km away - Coordinates: {place['lat']:.5f}, {place['lon']:.5f}")
                if place.get("source"):
                    st.markdown(f"[View verified Wikipedia source]({place['source']})")
            with right:
                st.link_button("Directions", maps, use_container_width=True)

def hotel_price_guide(city: str, budget: tuple[int, int], people: int, days: int, rooms: int, check_in: date) -> None:
    """Show transparent accommodation planning totals and a link to live hotel rates."""
    check_out = check_in + timedelta(days=days)
    total_low = budget[0] * rooms * days
    total_high = budget[1] * rooms * days
    date_label = f"{check_in.strftime('%d %b %Y')} to {check_out.strftime('%d %b %Y')}"
    search_query = f"Google Hotels {city} {date_label} {people} guests {rooms} rooms"
    live_rates_url = f"https://www.google.com/travel/search?q={quote_plus(search_query)}"

    with st.container(border=True):
        st.markdown(
            f"""
            <section class="price-guide">
              <h3>Hotel budget planner</h3>
              <p>Your selected range is <strong>INR {budget[0]:,} to INR {budget[1]:,} per room, per night</strong> for {rooms} room(s) across {days} night(s).</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        left, middle, right = st.columns(3)
        left.metric("Stay dates", date_label)
        middle.metric("Rooms x nights", f"{rooms} x {days}")
        right.metric("Accommodation plan", f"INR {total_low:,.0f} to INR {total_high:,.0f}")
        st.link_button("Compare live hotel prices for these dates", live_rates_url, use_container_width=True)
        st.caption(
            "Hotel rates change with dates, room type, taxes and availability. The range above is your planning budget; use the live comparison before booking."
        )


@st.cache_data(ttl=3600, show_spinner=False)
def itinerary(city, people, days, budget, rooms, check_in):
    check_out = check_in + timedelta(days=days)
    agent = create_agent(
        model=ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, max_retries=3),
        tools=[search_web],
    )
    prompt = (
        f"Act as a luxury travel concierge for {city}. Plan a trip for {people} people for {days} days, "
        f"from {check_in.strftime('%d %B %Y')} to {check_out.strftime('%d %B %Y')}. "
        "Use clear Markdown headings (###). "
        "List exactly 5 attractions with short, useful descriptions. "
        f"Recommend 5 suitable hotels inside the user's target budget of INR {budget[0]:,} to INR {budget[1]:,} per room per night. "
        "For every hotel give its name, likely star category, and why it suits the trip, but do NOT invent a live, confirmed, or exact hotel rate. "
        "Add a short 'Hotel pricing note' stating that rates must be checked live for the selected dates and availability. "
        f"Calculate the accommodation planning range as INR {budget[0]:,} to INR {budget[1]:,} x {rooms} room(s) x {days} night(s), "
        f"then calculate a clearly labelled estimated total trip cost using the midpoint of that accommodation range plus food for {people} people and a local-transport buffer."
    )
    with get_openai_callback():
        answer = agent.invoke({"messages": [("user", prompt)]})
    return answer["messages"][-1].content

>>>>>>> d946654c4c82f35f5ec0762ddfda75b3742d1ee1
with st.sidebar:
    st.markdown("## Trip settings")
    st.caption("Shape a journey worth retelling.")
    city = st.text_input("Enter destination", placeholder="e.g. Prayagraj, Goa, Maldives")
    people = st.number_input("Number of travelers", min_value=1, value=2)
    rooms = st.number_input("Rooms required", min_value=1, value=max(1, math.ceil(int(people) / 2)))
    trip_start = st.date_input("Check-in date", value=date.today() + timedelta(days=30), min_value=date.today())
    days = st.slider("Trip duration (nights)", 1, 14, 5)
    budget = st.slider("Target rate per room / night (INR)", 1000, 50000, (5000, 15000))
<<<<<<< HEAD
    
    # Save trip settings to session state
    if city.strip() and people > 0 and rooms > 0 and days > 0:
        trip_settings = TripSettings(
            destination=city.strip(),
            travelers=int(people),
            rooms=int(rooms),
            check_in=trip_start,
            duration_nights=int(days),
            price_range=budget
        )
        SessionStateManager.save_trip_settings(trip_settings)
    
    if st.button("Start a fresh plan"):
        st.cache_data.clear()
        st.session_state.clear()
        st.rerun()

# Hero section with rotating slogan
=======
    if st.button("Start a fresh plan"):
        st.cache_data.clear()
        st.session_state.pop("visitor_location", None)
        st.session_state.pop("location_error", None)
        st.rerun()

>>>>>>> d946654c4c82f35f5ec0762ddfda75b3742d1ee1
hero_slogan = html.escape(LUXURY_SLOGANS[int(time.time() // 4) % len(LUXURY_SLOGANS)])
st.markdown(
    f"""
    <section class="hero">
      <p class="eyebrow">A more beautiful way to travel</p>
      <h1 class="title">detour_maniac.ai</h1>
      <p class="tagline">{hero_slogan}</p>
    </section>
    """,
    unsafe_allow_html=True,
)

<<<<<<< HEAD
# Cost calculator component
if city.strip():
    city = city.strip()
    st.markdown(
        f'<section class="city-banner"><p class="eyebrow">Your destination edit</p><h2>Explore {html.escape(city)}</h2></section>',
        unsafe_allow_html=True
    )
    
    # Get trip settings from session state
    settings = SessionStateManager.get_trip_settings()
    
    if settings and settings.is_complete():
        # Calculate accommodation cost range
        accom_min, accom_max = HotelPricingModel.calculate_accommodation_cost(
            settings.price_range,
            settings.rooms,
            settings.duration_nights
        )
        
        # Calculate total trip estimate
        accom_midpoint = (accom_min + accom_max) // 2
        total_estimate = HotelPricingModel.estimate_total_trip_cost(
            accom_midpoint,
            settings.travelers,
            settings.duration_nights
        )
        
        check_out = settings.check_in + timedelta(days=settings.duration_nights)
        date_label = f"{settings.check_in.strftime('%d %b %Y')} to {check_out.strftime('%d %b %Y')}"
        
        with st.container(border=True):
            st.markdown(
                f"""
                <section class="price-guide">
                  <h3>Trip budget planner</h3>
                  <p>Your selected range is <strong>INR {settings.price_range[0]:,} to INR {settings.price_range[1]:,} per room, per night</strong> for {settings.rooms} room(s) across {settings.duration_nights} night(s).</p>
                </section>
                """,
                unsafe_allow_html=True,
            )
            left, middle, right = st.columns(3)
            left.metric("Stay dates", date_label)
            middle.metric("Rooms x nights", f"{settings.rooms} x {settings.duration_nights}")
            right.metric("Accommodation plan", f"INR {accom_min:,.0f} to INR {accom_max:,.0f}")
            
            st.markdown("#### Estimated total trip cost")
            st.metric("Total estimate", f"INR {total_estimate:,}")
            st.caption(
                f"Includes accommodation midpoint (INR {accom_midpoint:,}), "
                f"food for {settings.travelers} travelers (INR 2,000/person/day), "
                "and local transport buffer (INR 5,000)."
            )
        
        st.success("✅ Trip settings complete! Explore hotels, attractions, and maps using the sidebar navigation.")
        st.info("💡 Use the navigation menu on the left to visit Hotels, Attractions, and Maps pages.")
    else:
        st.info("Please complete trip settings in the sidebar to see cost estimates and enable navigation.")
else:
    st.info("Please enter a destination in the sidebar to begin planning your trip.")
=======
if city.strip():
    city = city.strip()
    st.markdown(f"<section class=\"city-banner\"><p class=\"eyebrow\">Your destination edit</p><h2>Explore {html.escape(city)}</h2></section>", unsafe_allow_html=True)
    with st.spinner(f"Finding highlights in {city}..."):
        places = attractions_for(city)
    attraction_background(city, places)
    hotel_price_guide(city, budget, int(people), int(days), int(rooms), trip_start)
    guide(places, city)
    if not GROQ_API_KEY:
        st.warning("Attraction previews and the location guide are ready. Add a Groq API key to generate the AI itinerary.")
        st.code('GROQ_API_KEY = "gsk_your_key_here"', language="toml")
        st.caption("Create .streamlit/secrets.toml from .streamlit/secrets.toml.example, add your key, then restart Streamlit.")
    else:
        with st.spinner(f"Organizing your {city} trip..."):
            try:
                plan = itinerary(city, int(people), int(days), budget, int(rooms), trip_start)
            except Exception as error:
                st.error("Rate limit reached or the itinerary could not be generated. Please try again.")
                st.caption(str(error))
            else:
                with st.container(border=True):
                    st.markdown(f"## Exclusive itinerary for {html.escape(city)}")
                    st.markdown(plan)
                    st.success("Trip plan generated successfully!")
else:
    st.info("Please enter a destination in the sidebar to begin.")
>>>>>>> d946654c4c82f35f5ec0762ddfda75b3742d1ee1
