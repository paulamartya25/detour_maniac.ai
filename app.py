import html
import math
import time
from datetime import date, timedelta

import streamlit as st

# Import utility modules
from utils.session_state import SessionStateManager, TripSettings
from utils.pricing import HotelPricingModel
from utils.styling import get_base_styles

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

LUXURY_SLOGANS = (
    "Chase horizons. Collect stories.",
    "Your next unforgettable chapter starts here.",
    "Go further, feel deeper, remember forever.",
    "Curated escapes for the beautifully curious.",
    "Leave with memories, not just photographs.",
)

# Sidebar with trip settings
with st.sidebar:
    st.markdown("## Trip settings")
    st.caption("Shape a journey worth retelling.")
    city = st.text_input("Enter destination", placeholder="e.g. Prayagraj, Goa, Maldives")
    people = st.number_input("Number of travelers", min_value=1, value=2)
    rooms = st.number_input("Rooms required", min_value=1, value=max(1, math.ceil(int(people) / 2)))
    trip_start = st.date_input("Check-in date", value=date.today() + timedelta(days=30), min_value=date.today())
    days = st.slider("Trip duration (nights)", 1, 14, 5)
    budget = st.slider("Target rate per room / night (INR)", 1000, 50000, (5000, 15000))

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
