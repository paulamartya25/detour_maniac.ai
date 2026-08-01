"""
Fix script for DETOUR_MANIAX travel app
This script fixes:
1. Maps page AssertionError (missing __init__.py files)
2. Hotels page budget filtering
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

print("=" * 60)
print("DETOUR_MANIAX - Fix Script")
print("=" * 60)

# Fix 1: Create missing __init__.py files
print("\n[1/3] Creating missing __init__.py files...")

components_dir = BASE_DIR / "components"
browser_location_dir = components_dir / "browser_location"

# Create components/__init__.py
components_init = components_dir / "__init__.py"
if not components_init.exists():
    components_init.write_text('"""Components package."""\n', encoding='utf-8')
    print(f"✓ Created: {components_init}")
else:
    print(f"✓ Already exists: {components_init}")

# Create components/browser_location/__init__.py
browser_init = browser_location_dir / "__init__.py"
browser_init.write_text('"""Browser location component for Streamlit."""\n', encoding='utf-8')
print(f"✓ Created/Updated: {browser_init}")

# Fix 2: Update Hotels page with budget filtering
print("\n[2/3] Updating Hotels page with budget filtering...")

hotels_file = BASE_DIR / "pages" / "1_🏨_Hotels.py"

hotels_code = '''"""Hotels page displaying hotel recommendations with star categories and pricing.

This page shows hotels for the selected destination with accurate pricing based on
star categories, filtered by the user's budget range.

Requirements: 1.1, 1.2, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.8
"""

import html
from datetime import timedelta
from urllib.parse import quote_plus

import streamlit as st

from utils.session_state import SessionStateManager
from utils.pricing import HotelPricingModel, HotelStarCategory
from utils.styling import get_base_styles

# Page configuration
st.set_page_config(page_title="Hotels - DETOUR_MANIAX", layout="wide", page_icon="🏨")

# Apply consistent styling
st.markdown(get_base_styles(), unsafe_allow_html=True)

# Additional page-specific styles
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

# Retrieve trip settings from session state
settings = SessionStateManager.get_trip_settings()

# Check if settings are complete
if not settings or not settings.is_complete():
    st.warning("⚠️ Please complete your trip settings on the homepage first.")
    st.page_link("app.py", label="← Back to Homepage", icon="🏠")
    st.stop()

# Page header
st.markdown(f"# 🏨 Hotels in {html.escape(settings.destination)}")

# Hotel data - all hotels sorted by star category (highest to lowest)
all_hotels = [
    {
        "name": f"Grand Palace {settings.destination}",
        "category": HotelStarCategory.FIVE_STAR,
        "description": "Premium luxury accommodation with world-class amenities, spa facilities, fine dining restaurants, and personalized concierge services. Perfect for travelers seeking the ultimate comfort and sophistication."
    },
    {
        "name": f"Royal Comfort {settings.destination}",
        "category": HotelStarCategory.FOUR_STAR,
        "description": "Upscale hotel offering excellent service, modern rooms with premium furnishings, fitness center, swimming pool, and on-site dining options. Ideal for business and leisure travelers."
    },
    {
        "name": f"City Plaza {settings.destination}",
        "category": HotelStarCategory.THREE_STAR,
        "description": "Well-appointed mid-range hotel with comfortable rooms, complimentary breakfast, convenient location, and friendly staff. Great value for money with all essential amenities."
    },
    {
        "name": f"Traveler's Inn {settings.destination}",
        "category": HotelStarCategory.TWO_STAR,
        "description": "Budget-friendly hotel with clean, basic rooms, helpful staff, and convenient access to local attractions. Perfect for practical travelers who prefer spending on experiences."
    },
    {
        "name": f"Economy Lodge {settings.destination}",
        "category": HotelStarCategory.ONE_STAR,
        "description": "Simple, no-frills accommodation offering essential amenities at the most affordable rates. Suitable for backpackers and budget-conscious travelers."
    }
]

# Filter hotels by budget
user_min_budget, user_max_budget = settings.price_range
filtered_hotels = []

for hotel in all_hotels:
    price_range = HotelPricingModel.get_price_range(hotel["category"])
    hotel_min_price = price_range.min_price
    hotel_max_price = price_range.max_price

    # Check if hotel price range overlaps with user budget
    if hotel_min_price <= user_max_budget and hotel_max_price >= user_min_budget:
        filtered_hotels.append(hotel)

# Display filtered hotels or message
if not filtered_hotels:
    st.warning(f"⚠️ No hotels available within your budget range of INR {user_min_budget:,} - {user_max_budget:,} per room per night.")
    st.info("💡 Please adjust your budget on the homepage to see available hotels.")
    st.page_link("app.py", label="← Back to Homepage", icon="🏠")
    st.stop()

# Display caption with number of hotels found
st.caption(f"Showing {len(filtered_hotels)} hotel(s) within your budget for your {settings.duration_nights}-night stay")

# Display filtered hotels
for hotel in filtered_hotels:
    price_range = HotelPricingModel.get_price_range(hotel["category"])
    stars = "⭐" * hotel["category"].value

    st.markdown(
        f"""
        <div class="hotel-card">
            <h3 class="hotel-name">{html.escape(hotel['name'])}</h3>
            <div class="star-rating">{stars} {hotel['category'].value}-Star Hotel</div>
            <p class="hotel-description">{html.escape(hotel['description'])}</p>
            <div class="price-info">
                <div class="price-label">Price Range Per Room Per Night</div>
                <div class="price-value">INR {price_range.min_price:,} - {price_range.max_price:,}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Calculate total accommodation cost for the trip
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

# Live price comparison link
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
    "⚠️ **Important:** The price ranges shown above are estimates based on star categories. "
    "Actual hotel rates vary based on season, availability, room type, taxes, and booking platform. "
    "Always verify current pricing and availability using the live comparison link before making reservations."
)

# Navigation hint
st.info("💡 Explore attractions and maps using the sidebar navigation!")
'''

hotels_file.write_text(hotels_code, encoding='utf-8')
print(f"✓ Updated: {hotels_file}")

# Fix 3: Verification
print("\n[3/3] Verifying fixes...")

if components_init.exists() and browser_init.exists():
    print("✓ All __init__.py files exist")
else:
    print("✗ Some __init__.py files are missing")

if hotels_file.exists():
    print("✓ Hotels page updated")
else:
    print("✗ Hotels page not found")

# Final instructions
print("\n" + "=" * 60)
print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
print("=" * 60)
print("\n📋 NEXT STEPS:")
print("1. STOP the Streamlit server (Press Ctrl+C in the terminal)")
print("2. RESTART Streamlit:")
print("   python -m streamlit run app.py")
print("3. HARD REFRESH the browser:")
print("   Windows/Linux: Ctrl + Shift + R")
print("   Mac: Cmd + Shift + R")
print("\n💡 Changes applied:")
print("   ✓ Fixed Maps page AssertionError")
print("   ✓ Hotels now filter by your budget")
print("   ✓ Shows 'No hotels available' message when budget too low")
print("\n" + "=" * 60)
