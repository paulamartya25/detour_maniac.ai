"""Hotels page with REAL hotel names."""

import html
from datetime import timedelta
from urllib.parse import quote_plus

import streamlit as st

from utils.session_state import SessionStateManager
from utils.pricing import HotelPricingModel
from utils.styling import get_base_styles
from utils.hotels import get_real_hotels

st.set_page_config(page_title="Hotels - DETOUR_MANIAX", layout="wide", page_icon="🏨")
st.markdown(get_base_styles(), unsafe_allow_html=True)

# Page-specific styles
st.markdown("""
<style>
.hotel-card {
    background: rgba(255, 253, 249, .97);
    border: 1px solid rgba(255, 255, 255, .9);
    border-left: 4px solid #d66745;
    border-radius: 20px;
    box-shadow: 0 16px 42px rgba(23, 45, 68, .18);
    backdrop-filter: blur(14px);
    padding: 1.8rem;
    margin-bottom: 1.5rem;
}
.hotel-name {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: #0b172a;
    margin: 0 0 0.5rem 0;
}
.hotel-area {
    color: #6b7280;
    font-size: 0.95rem;
    margin-bottom: 0.75rem;
}
.star-rating {
    font-size: 1.1rem;
    margin-bottom: 0.75rem;
    color: #bf821d;
}
.hotel-description {
    color: #374151;
    line-height: 1.6;
    margin-bottom: 1rem;
}
.price-info {
    background: linear-gradient(115deg, rgba(255,247,231,.95), rgba(255,255,255,.94));
    border: 1px solid rgba(191,130,29,.25);
    border-radius: 12px;
    padding: 1rem;
    margin-top: 1rem;
}
.price-label {
    font-size: 0.85rem;
    font-weight: 600;
    color: #6e4505;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.price-value {
    font-size: 1.4rem;
    font-weight: 700;
    color: #111827;
}
</style>
""", unsafe_allow_html=True)

# Retrieve trip settings
settings = SessionStateManager.get_trip_settings()

if not settings or not settings.is_complete():
    st.warning("⚠️ Please complete your trip settings on the homepage first.")
    st.page_link("app.py", label="← Back to Homepage", icon="🏠")
    st.stop()

# Page header
st.markdown(f"# 🏨 Hotels in {html.escape(settings.destination)}")

# Get REAL hotels for this city filtered by budget
real_hotels = get_real_hotels(settings.destination, settings.price_range)

if not real_hotels:
    st.warning(f"⚠️ No hotels available in {settings.destination} within your budget range of INR {settings.price_range[0]:,} - {settings.price_range[1]:,} per room per night.")
    st.info("💡 Try adjusting your budget on the homepage to see available hotels.")
    st.page_link("app.py", label="← Back to Homepage", icon="🏠")
    st.stop()

# Display caption
st.caption(f"Showing {len(real_hotels)} real hotel(s) in {settings.destination} within your budget for your {settings.duration_nights}-night stay")

# Hotel descriptions by star category
HOTEL_DESCRIPTIONS = {
    5: "Luxury accommodation with world-class amenities, spa facilities, fine dining restaurants, and personalized concierge services. Perfect for travelers seeking the ultimate comfort.",
    4: "Upscale hotel offering excellent service, modern rooms with premium furnishings, fitness center, swimming pool, and on-site dining options. Ideal for business and leisure travelers.",
    3: "Well-appointed mid-range hotel with comfortable rooms, complimentary breakfast, convenient location, and friendly staff. Great value for money with all essential amenities.",
    2: "Budget-friendly hotel with clean, basic rooms, helpful staff, and convenient access to local attractions. Perfect for practical travelers who prefer spending on experiences.",
    1: "Simple, no-frills accommodation offering essential amenities at affordable rates. Suitable for backpackers and budget-conscious travelers.",
}

# Display real hotels
for hotel in real_hotels:
    price_range = HotelPricingModel.get_price_range(hotel["category"])
    stars = "⭐" * hotel["category"].value
    description = HOTEL_DESCRIPTIONS[hotel["category"].value]

    st.markdown(
        f"""
        <div class="hotel-card">
            <h3 class="hotel-name">{html.escape(hotel['name'])}</h3>
            <div class="hotel-area">📍 {html.escape(hotel['area'])}, {html.escape(settings.destination)}</div>
            <div class="star-rating">{stars} {hotel['category'].value}-Star Hotel</div>
            <p class="hotel-description">{html.escape(description)}</p>
            <div class="price-info">
                <div class="price-label">Price Range Per Room Per Night</div>
                <div class="price-value">INR {price_range.min_price:,} - {price_range.max_price:,}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Budget summary
st.markdown("---")
st.markdown("### Your Accommodation Budget")

accom_min, accom_max = HotelPricingModel.calculate_accommodation_cost(
    settings.price_range,
    settings.rooms,
    settings.duration_nights
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Your Budget Range", f"INR {settings.price_range[0]:,} - {settings.price_range[1]:,}", help="Per room, per night")
with col2:
    st.metric("Total Rooms", f"{settings.rooms}")
with col3:
    st.metric("Total Nights", f"{settings.duration_nights}")

st.metric("Total Accommodation Cost", f"INR {accom_min:,} - {accom_max:,}", help="Total cost for all rooms and nights")

# Live price comparison
st.markdown("---")
st.markdown("### Compare Live Prices")

check_out = settings.check_in + timedelta(days=settings.duration_nights)
search_query = (
    f"Hotels {settings.destination} "
    f"{settings.check_in.strftime('%Y-%m-%d')} to {check_out.strftime('%Y-%m-%d')} "
    f"{settings.travelers} guests {settings.rooms} rooms"
)
comparison_url = f"https://www.google.com/travel/search?q={quote_plus(search_query)}"

st.link_button("🔍 Compare Live Hotel Prices for Your Dates", comparison_url, use_container_width=True)

st.caption(
    "⚠️ **Important:** Actual hotel rates vary based on season, availability, room type, taxes, and booking platform. "
    "Always verify current pricing and availability using the live comparison link before making reservations."
)

st.info("💡 Explore attractions and maps using the sidebar navigation!")
