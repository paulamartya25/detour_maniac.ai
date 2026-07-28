import html
import json
import math
import os
import time
from pathlib import Path

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
ROTATION_MS = 4000
FALLBACK_IMAGE = "https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=1400&q=85"

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
.stApp{background:linear-gradient(#ffffff33,#ffffff33),url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1920&q=80") center/cover fixed}
h1,h2,h3,h4,p,div,span{font-family:Arial,sans-serif;color:#000!important}.title{text-align:center;font-size:4rem}.tagline{text-align:center;font-style:italic;font-size:1.2rem;font-weight:bold}.card{background:#ffffffe8;border-radius:20px;padding:32px;box-shadow:0 8px 24px #0004}
[data-testid="stSidebar"]{background:#001f33e8}[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3,[data-testid="stSidebar"] p,[data-testid="stSidebar"] label,[data-testid="stSidebar"] span{color:white!important}
</style>
""", unsafe_allow_html=True)


@tool
def search_web(query: str):
    """Search the web for current travel information."""
    return DuckDuckGoSearchRun().run(query)


@st.cache_data(ttl=86400, show_spinner=False)
def attractions_for(city: str) -> list[dict]:
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{city} tourist attractions", "gsrnamespace": 0, "gsrlimit": 12,
        "prop": "pageimages|extracts|coordinates|pageprops", "piprop": "thumbnail",
        "pithumbsize": 1400, "exintro": 1, "explaintext": 1, "exsentences": 2,
    }
    try:
        response = requests.get(WIKIPEDIA_API, params=params, timeout=10,
                                headers={"User-Agent": "detour-maniax/1.0 travel-planner"})
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {}).values()
    except (requests.RequestException, ValueError):
        return []

    places = []
    for page in sorted(pages, key=lambda item: int(item.get("index", 9999))):
        if "disambiguation" in page.get("pageprops", {}):
            continue
        name = page.get("title", "").strip()
        if not name:
            continue
        coordinate = page.get("coordinates", [{}])[0]
        places.append({
            "name": name,
            "description": page.get("extract", "").strip() or "A local highlight worth exploring.",
            "image": page.get("thumbnail", {}).get("source"),
            "lat": coordinate.get("lat"),
            "lon": coordinate.get("lon"),
        })
    places.sort(key=lambda item: item["image"] is None)
    return places[:6]


@st.fragment(run_every="4s")
def attraction_background(city: str, places: list[dict]) -> None:
    """Rotate the selected destination's attraction images as the app background."""
    if not places:
        st.info(f"Attraction photos for {city} are temporarily unavailable. Your itinerary can still be generated.")
        return

    current_index = int(time.time() // (ROTATION_MS / 1000)) % len(places)
    current = places[current_index]
    image_url = html.escape(current["image"] or FALLBACK_IMAGE, quote=True)
    attraction_name = html.escape(current["name"])
    summary = html.escape(" ".join(current["description"].split())[:320])

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 16, 32, .50), rgba(0, 16, 32, .55)), url("{image_url}") !important;
            background-position: center !important;
            background-size: cover !important;
            background-attachment: fixed !important;
        }}
        .destination-attraction {{
            background: rgba(3, 20, 34, .76);
            border: 1px solid rgba(210, 245, 255, .45);
            border-radius: 18px;
            box-shadow: 0 12px 30px rgba(0, 0, 0, .26);
            color: white !important;
            margin: 0 0 1rem;
            padding: 1.25rem 1.5rem;
        }}
        .destination-attraction * {{ color: white !important; }}
        .destination-attraction .eyebrow {{
            color: #b9efff !important;
            font-size: .8rem;
            font-weight: 700;
            letter-spacing: .12rem;
            margin: 0 0 .35rem;
            text-transform: uppercase;
        }}
        .destination-attraction h2 {{ font-size: 1.8rem; margin: 0 0 .45rem; }}
        .destination-attraction p {{ line-height: 1.5; margin: 0; }}
        </style>
        <section class="destination-attraction">
          <p class="eyebrow">Now showing: {html.escape(city)}</p>
          <h2>{attraction_name}</h2>
          <p>{summary}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.caption("The attraction photo in the background changes automatically every 4 seconds.")

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
        st.caption("Share your browser location above to see distances from your current position, your GPS coordinates, and the destination attraction map.")
        return

    mappable = [
        place for place in places
        if isinstance(place.get("lat"), (int, float))
        and isinstance(place.get("lon"), (int, float))
    ]
    if not mappable:
        st.info("Location shared. Map coordinates are not available for these attractions yet.")
        return

    st.success("Location shared. Distances below are from your current position.")
    st.caption(f"Your current coordinates: {location['lat']:.5f}, {location['lon']:.5f}. Distances are direct estimates; Directions opens a route and travel-time estimate.")

    coordinate_rows = [
        {
            "place": place["name"],
            "latitude": float(place["lat"]),
            "longitude": float(place["lon"]),
            "color": "#ef5b5b",
            "size": 140,
        }
        for place in mappable
    ]
    map_data = pd.DataFrame(coordinate_rows)

    st.markdown(f"#### {html.escape(city)} attraction map")
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
    st.dataframe(
        coordinate_table.rename(
            columns={
                "place": "Attraction",
                "latitude": "Latitude",
                "longitude": "Longitude",
            }
        ),
        hide_index=True,
        use_container_width=True,
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
            st.caption(f"About {km:.1f} km away · Coordinates: {place['lat']:.5f}, {place['lon']:.5f}")
        with right:
            st.link_button("Directions", maps, use_container_width=True)

@st.cache_data(ttl=3600, show_spinner=False)
def itinerary(city, people, days, budget):
    agent = create_agent(
        model=ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, max_retries=3),
        tools=[search_web],
    )
    prompt = (
        f"Act as a luxury travel concierge for {city}. Plan a trip for {people} people for {days} days. "
        "Use clear Markdown headings (###). "
        "List exactly 5 attractions with descriptions; recommend 5 hotels in the range "
        f"{budget[0]}-{budget[1]} INR with name, star rating and price; then calculate a total trip cost "
        f"using (average hotel price * {days} nights) + (food * {people} people * {days} days) + local travel buffer."
    )
    with get_openai_callback():
        answer = agent.invoke({"messages": [("user", prompt)]})
    return answer["messages"][-1].content


with st.sidebar:
    st.markdown("## Trip Settings")
    city = st.text_input("Enter Destination", placeholder="e.g. Prayagraj, Goa, Maldives")
    people = st.number_input("Number of Travelers", min_value=1, value=2)
    days = st.slider("Trip Duration (Days)", 1, 14, 5)
    budget = st.slider("Hotel Budget (INR)", 1000, 50000, (5000, 15000))
    if st.button("Reset Plan"):
        st.cache_data.clear()
        st.session_state.pop("visitor_location", None)
        st.session_state.pop("location_error", None)
        st.rerun()

st.markdown("<h1 class='title'>detour_maniac.ai</h1>", unsafe_allow_html=True)
st.markdown("<p class='tagline'>Collect moments, not things.</p>", unsafe_allow_html=True)

if city.strip():
    city = city.strip()
    st.markdown(f"## Explore {html.escape(city)}")
    with st.spinner(f"Finding highlights in {city}..."):
        places = attractions_for(city)
    attraction_background(city, places)
    guide(places, city)
    if not GROQ_API_KEY:
        st.warning("Attraction previews and the location guide are ready. Add a Groq API key to generate the AI itinerary.")
        st.code('GROQ_API_KEY = "gsk_your_key_here"', language="toml")
        st.caption("Create .streamlit/secrets.toml from .streamlit/secrets.toml.example, add your key, then restart Streamlit.")
    else:
        with st.spinner(f"Organizing your {city} trip..."):
            try:
                plan = itinerary(city, int(people), int(days), budget)
            except Exception as error:
                st.error("Rate limit reached or the itinerary could not be generated. Please try again.")
                st.caption(str(error))
            else:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f"## Exclusive Itinerary for {html.escape(city)}")
                st.markdown(plan)
                st.success("Trip plan generated successfully!")
                st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("Please enter a destination in the sidebar to begin.")