<img width="1600" height="640" alt="WhatsApp Image 2026-07-28 at 13 15 13" src="https://github.com/user-attachments/assets/4dcf6df4-1e3e-41b8-8674-180135528305" />
<img width="1586" height="619" alt="WhatsApp Image 2026-07-28 at 13 16 33" src="https://github.com/user-attachments/assets/68f66772-7394-4169-b296-854e30a2cfa5" />
🚀 Overview

detour_maniac.ai is a next-generation travel planning application designed to take the stress out of trip planning. Powered by the blazing-fast Llama 3.3 model on Groq and orchestrated by LangChain, this agentic AI creates personalized, structured travel itineraries in seconds.

Unlike a generic chatbot, detour_maniac.ai uses live web search tools to pull real, current information — hotel prices, verified attractions, and estimated travel costs — so your plan is grounded in reality, not hallucinated.

The app has been redesigned around a clean "Trip Settings" workflow: set your destination, traveler count, room requirements, dates, and budget in the sidebar, and get back a curated, editorial-style breakdown of your destination.

✨ Key Features
🧭 Guided Trip Settings: A dedicated sidebar to configure destination, number of travelers, rooms required, check-in date, trip duration, and target rate per room (INR) via an intuitive slider.
🌍 Smart Itinerary Generation: Automatically generates a structured plan including:
Top Places to Visit: Curated, verified attractions (monuments, cathedrals, parks, and more) with descriptive context.
Recommended Hotels: Real-time search for hotels within your specified budget range.
💰 Total Cost Breakdown: A mathematical estimate covering hotels, food, and local travel.
✅ Verified Attractions: Each recommended spot is tagged as a "Verified Attraction" and comes with a short, sourced description rather than a generic blurb.
⚡ Blazing Fast Inference: Built on Groq's LPU Engine, delivering results at 300+ tokens/second.
🔎 Real-Time Data: Integrated with DuckDuckGo Search to find current information on the web.
🎨 Editorial UI: A redesigned, magazine-style interface with a full-bleed destination photo, serif headlines, and warm, muted tones.
🛠️ Tech Stack
Frontend: Streamlit
LLM Orchestration: LangChain
Model Provider: Groq (Llama-3.3-70b-versatile)
Tools: DuckDuckGo Search (for live web browsing)
Language: Python
⚙️ Installation & Setup

Follow these steps to run the project locally on your machine.

1. Clone the Repository
bash
git clone https://github.com/paulamartya25/detour_maniac.ai.git
cd detour_maniac.ai
2. Create a Virtual Environment
bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
pip install -r requirements.txt
4. Configure Environment Variables

Create a .env file in the project root and add your Groq API key:

env
GROQ_API_KEY=your_groq_api_key_here
5. Run the App
bash
streamlit run app.py

The app will open automatically in your browser at http://localhost:8501.

📖 Usage
Open the Trip settings panel on the left.
Enter your destination, number of travelers, and rooms required.
Pick your check-in date and trip duration (in nights).
Set your target rate per room/night (INR) using the slider.
Click generate and let detour_maniac.ai build your itinerary — complete with verified attractions, hotel picks, and a full cost breakdown.
