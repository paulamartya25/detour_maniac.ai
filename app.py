import html
import json
import math
import os
from pathlib import Path

import requests
import streamlit as st
import streamlit.components.v1 as components
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

try:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

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


def carousel(city: str, places: list[dict]) -> None:
    if not places:
        st.info(f"Attraction photos for {city} are temporarily unavailable. Your itinerary can still be generated.")
        return
    slides = [{"name": p["name"], "description": p["description"], "image": p["image"] or FALLBACK_IMAGE} for p in places]
    data = json.dumps(slides).replace("</", "<\\/")
    safe_city = html.escape(city)
    components.html(f"""
    <style>
    *{{box-sizing:border-box}}body{{margin:0;font-family:Arial}}.box{{height:410px;overflow:hidden;position:relative;border-radius:18px;background:#06324c}}img{{width:100%;height:100%;object-fit:cover;transition:opacity .4s}}img.f{{opacity:.2}}.shade{{position:absolute;inset:0;background:linear-gradient(90deg,#001827c7,#00182708)}}
    .copy{{position:absolute;left:32px;right:32px;bottom:30px;max-width:700px}}.small{{color:#b9efff;letter-spacing:1.5px;font-weight:bold;font-size:12px}}h2,p{{color:#fff}}h2{{font-size:32px;margin:8px 0}}p{{line-height:1.45}}.dots{{position:absolute;right:22px;bottom:15px;display:flex;gap:6px}}i{{width:9px;height:9px;border-radius:9px;background:#ffffff88}}i.on{{width:22px;background:white}}
    </style>
    <div class="box" aria-label="Rotating tourist attractions in {safe_city}"><img id="photo" alt="Tourist attraction"><div class="shade"></div><div class="copy"><span class="small">DISCOVER {safe_city}</span><h2 id="name"></h2><p id="description"></p></div><div id="dots" class="dots"></div></div>
    <script>
    const slides={data},photo=document.getElementById("photo"),name=document.getElementById("name"),description=document.getElementById("description"),dots=document.getElementById("dots");let active=0;
    slides.forEach(()=>{{let dot=document.createElement("i");dots.appendChild(dot)}});
    function show(n,first=false){{let item=slides[n];if(!first)photo.classList.add("f");setTimeout(()=>{{photo.src=item.image;photo.alt=item.name;name.textContent=item.name;description.textContent=item.description;[...dots.children].forEach((dot,i)=>dot.classList.toggle("on",i===n));photo.classList.remove("f")}},first?0:200)}}
    show(active,true);setInterval(()=>{{active=(active+1)%slides.length;show(active)}},{ROTATION_MS});
    </script>
    """, height=425, scrolling=False)
    st.caption("Attraction preview changes automatically every 4 seconds. Photos and summaries are sourced from Wikipedia when available.")


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


def guide(places):
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
        st.caption("Share your browser location above to see approximate distances from your current position. Your coordinates stay only in this session.")
        return

    mappable = [p for p in places if isinstance(p.get("lat"), (int, float)) and isinstance(p.get("lon"), (int, float))]
    if not mappable:
        st.info("Location shared. Map coordinates are not available for these attractions yet.")
        return
    st.success("Location shared. Distances below are from your current position.")
    st.caption("These are direct (straight-line) estimates. Directions opens a route and travel-time estimate.")
    for place in mappable:
        km = distance_km(location["lat"], location["lon"], place["lat"], place["lon"])
        maps = f"https://www.google.com/maps/dir/?api=1&origin={location['lat']},{location['lon']}&destination={place['lat']},{place['lon']}"
        left, right = st.columns([3, 1])
        with left:
            st.markdown(f"**{html.escape(place['name'])}**")
            st.caption(f"About {km:.1f} km away")
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
    carousel(city, places)
    guide(places)
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