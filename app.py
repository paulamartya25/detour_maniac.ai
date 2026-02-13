import streamlit as st
import os
import random
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_community.callbacks import get_openai_callback

# --- 1. SECURE SETUP ---
try:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets!")
    st.stop()

st.set_page_config(page_title="DETOUR_MANIAX", layout="wide")

# --- 2. CATCHY QUOTES ---
def get_travel_quote():
    quotes = [
        "“The ocean stirs the heart, inspires the imagination and brings eternal joy to the soul.”",
        "“To travel is to live.” – Hans Christian Andersen",
        "“Salt water cures all wounds.”",
        "“Travel is the only thing you buy that makes you richer.”",
        "“Collect moments, not things.”",
        "“Meet me where the sky touches the sea.”",
        "“Live with no excuses and travel with no regrets.”"
    ]
    return random.choice(quotes)

# --- 3. "DETOUR_MANIAX" SEA THEME UI ---
def apply_fancy_design():
    # Vibrant Sea/Beach Background
    bg_url = "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1920&q=80"

    st.markdown(
        f"""
        <style>
        /* Import Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Poppins:wght@400;600&display=swap');

        /* 1. BACKGROUND */
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.2)), url("{bg_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* 2. FORCE MAIN TEXT TO BE BLACK (Fixes visibility issue) */
        h1, h2, h3, h4, h5, h6, p, li, div, span {{
            color: #000000 !important; /* Pure Black */
            font-family: 'Poppins', sans-serif;
            text-shadow: none !important; /* Remove shadow for crisp look */
        }}

        /* 3. MAIN TITLE CUSTOMIZATION */
        .main-title {{
            font-family: 'Cinzel', serif !important;
            font-size: 4rem;
            text-align: center;
            font-weight: 800;
            color: #000000 !important;
            margin-bottom: 5px;
        }}
        
        /* Quote Text */
        .quote-text {{
            text-align: center;
            font-style: italic;
            color: #000000 !important;
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 30px;
        }}

        /* 4. WHITE GLASS CARD */
        .travel-card {{
            background: rgba(255, 255, 255, 0.90); /* High Opacity White */
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            margin-top: 10px;
            border: 2px solid rgba(255, 255, 255, 1);
        }}

        /* 5. HEADINGS INSIDE CARD */
        .travel-card h1, .travel-card h2, .travel-card h3 {{
            color: #003366 !important; /* Navy Blue for Section Headers */
            font-family: 'Cinzel', serif !important;
            border-bottom: 3px solid #00bfff;
            padding-bottom: 8px;
            margin-top: 25px;
            font-weight: 700;
        }}

        /* 6. SIDEBAR STYLING (Must remain White/Light) */
        [data-testid="stSidebar"] {{
            background-color: rgba(0, 20, 40, 0.9); /* Dark Sidebar */
            border-right: 1px solid rgba(255,255,255,0.2);
        }}
        
        /* Force Sidebar Text to be White (Overrides the global Black rule above) */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{
            color: #FFFFFF !important;
            font-family: 'Poppins', sans-serif;
        }}
        
        /* Sidebar Inputs */
        [data-testid="stSidebar"] input, [data-testid="stSidebar"] div[data-baseweb="select"] > div {{
            background-color: rgba(255, 255, 255, 0.15) !important;
            color: white !important;
            border: 1px solid white !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# --- 4. ROBUST SEARCH TOOL ---
@tool
def search_web(query: str):
    """
    Useful for searching the internet. 
    Always pass the query as a simple string.
    """
    search = DuckDuckGoSearchRun()
    return search.run(query)

# --- 5. SIDEBAR SETTINGS ---
apply_fancy_design()

with st.sidebar:
    st.markdown("## ✈️ Trip Settings")
    
    city = st.text_input("Enter Destination", placeholder="e.g. Maldives, Goa")
    
    st.markdown("### 👥 Travelers & Duration")
    num_people = st.number_input("Number of Travelers", min_value=1, value=2)
    num_days = st.slider("Trip Duration (Days)", 1, 14, 5)
    
    st.markdown("### 💰 Budget Per Night")
    hotel_budget = st.slider("Hotel Budget (INR)", 1000, 50000, (5000, 15000))
    
    st.divider()
    if st.button("🔄 Reset Plan"):
        st.rerun()

# --- 6. MAIN APP LOGIC ---

# Title & Quote
st.markdown("<h1 class='main-title'>detour_maniac.ai</h1>", unsafe_allow_html=True)
st.markdown(f"<p class='quote-text'>{get_travel_quote()}</p>", unsafe_allow_html=True)

if city:
    # Initialize Llama 3.3 (Hardcoded)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.1,
        max_retries=3
    )

    tools = [search_web]
    agent = create_agent(model=llm, tools=tools)

    # --- STRUCTURED PROMPT ---
    query = (
        f"Act as a luxury travel concierge for {city}. "
        f"Plan a trip for {num_people} people for {num_days} days. "
        f"You MUST format the output using clear Markdown Headings (###).\n\n"
        
        f"### Section 1: 🏛️ Top 5 Places to Visit\n"
        f"- List exactly 5 distinct places (Monuments, Parks, Museums, Beaches).\n"
        f"- One sentence description for each.\n\n"
        
        f"### Section 2: 🏨 Recommended Hotels\n"
        f"- Find 5 hotels in {city} within {hotel_budget[0]}-{hotel_budget[1]} INR range.\n"
        f"- Show Name, Star Rating, and Price Per Night.\n\n"
        
        f"### Section 3: 💰 Total Trip Cost Breakdown\n"
        f"- Calculate the Total Estimated Cost for the entire trip for {num_people} people.\n"
        f"- **Formula**: (Avg Hotel Price * {num_days} nights) + (Approx Food Cost * {num_people} people * {num_days} days) + (Local Travel Buffer). "
        f"- Assume reasonable food costs.\n"
        f"- Display it clearly."
    )

    # UPDATED SPINNER TEXT
    with st.spinner(f"✨ Organizing your {city} trip..."):
        try:
            # --- AI SEARCH ---
            with get_openai_callback() as cb:
                response = agent.invoke({"messages": [("user", query)]})
                
                # --- DISPLAY IN CARD ---
                st.markdown('<div class="travel-card">', unsafe_allow_html=True)
                st.markdown(f"<h2 style='text-align:center; border:none; color:#004d99 !important;'>✨ Exclusive Itinerary for {city}</h2>", unsafe_allow_html=True)
                st.markdown("<hr style='border-color: #00bfff;'>", unsafe_allow_html=True)
                
                st.markdown(response["messages"][-1].content)
                
                st.success(f"✅ Trip Plan Generated Successfully!")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Stats
                st.caption(f"We hope your trip becomes a memorable one..")

        except Exception as e:
            if "429" in str(e):
                st.error("🚨 Rate Limit Reached! The AI is busy right now. Please wait a moment or try again tomorrow.")
            else:
                st.error("⚠️ The AI got confused. Please try again.")
                st.error(f"Debug Info: {e}")

else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("👈 Please enter a destination in the sidebar to begin.")
