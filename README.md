# 🌍 DETOUR_MANIAX - AI-Powered Travel Planner

A modern, multi-page Streamlit application for intelligent travel planning with budget-aware hotel recommendations, verified attractions, and GPS-based navigation.

## ✨ Features

### 🏠 Homepage
- Interactive cost calculator
- Trip budget estimation
- Session state management across pages
- Rotating travel slogans

### 🏨 Hotels Page
- Budget-filtered hotel recommendations (1-5 star categories)
- Accurate pricing by star category (INR):
  - 1-Star: ₹1,000 - ₹2,500
  - 2-Star: ₹2,500 - ₹5,000
  - 3-Star: ₹5,000 - ₹10,000
  - 4-Star: ₹10,000 - ₹20,000
  - 5-Star: ₹20,000 - ₹50,000
- Live price comparison integration
- Total accommodation cost calculator

### 🎭 Attractions Page
- Wikipedia-verified attractions within 45km
- High-resolution images (1800px)
- Clean, card-based UI with white background
- Distance filtering from destination

### 🗺️ Maps Page
- Interactive map with attraction markers
- **GPS Location Features:**
  - Browser geolocation integration
  - City search for coordinates
  - Manual coordinate entry
- Distance calculations from your location
- Google Maps navigation integration

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

1. Clone the repository:
\\\ash
git clone https://github.com/paulamartya25/detour_maniac.ai.git
cd detour_maniac.ai
\\\

2. Create virtual environment:
\\\ash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\\\

3. Install dependencies:
\\\ash
pip install -r requirements.txt
\\\

4. Run the application:
\\\ash
streamlit run app.py
\\\

5. Open your browser to http://localhost:8501

## 🧪 Running Tests

\\\ash
# Run all tests
pytest

# Run with coverage
pytest --cov=utils --cov-report=html

# Run specific test file
pytest tests/test_pricing.py -v
\\\

## 📁 Project Structure

\\\
detour_maniac.ai/
├── app.py                      # Homepage
├── config.py                   # Configuration & constants
├── requirements.txt            # Dependencies
├── pages/
│   ├── 1_🏨_Hotels.py         # Hotels page
│   ├── 2_🎭_Attractions.py    # Attractions page
│   └── 3_🗺️_Maps.py           # Maps page
├── utils/
│   ├── session_state.py       # Session management
│   ├── pricing.py             # Hotel pricing logic
│   ├── styling.py             # UI styling
│   ├── attractions.py         # Attraction filtering
│   ├── calculations.py        # Distance calculations
│   └── errors.py              # Error handling
├── components/
│   └── browser_location/      # GPS component
└── tests/
    ├── test_pricing.py        # Pricing tests
    ├── test_calculations.py   # Calculation tests
    └── test_errors.py         # Error handling tests
\\\

## 🏗️ Architecture

### Multi-Page Design
- **Homepage**: Trip settings and cost calculator
- **Hotels**: Budget-filtered recommendations
- **Attractions**: Verified tourist spots
- **Maps**: Interactive navigation

### Key Design Patterns
- **Session State Management**: Trip settings persist across pages
- **Error Handling**: Graceful degradation with user feedback
- **Caching**: API responses cached with appropriate TTLs
- **Validation**: Input validation for all user inputs
- **Separation of Concerns**: Utility modules for reusability

### Technologies
- **Frontend**: Streamlit
- **Data**: Wikipedia API, Nominatim (OpenStreetMap)
- **Geolocation**: streamlit-js-eval
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, flake8, mypy

## 🌟 Key Features

### Budget-Aware Filtering
Hotels are filtered based on user's budget range. Only hotels within the specified price range are displayed.

### GPS Integration
Three methods to set location:
1. **Browser GPS**: One-click location fetching
2. **City Search**: Auto-find coordinates by city name
3. **Manual Entry**: Enter coordinates directly

### Distance Calculations
Uses Haversine formula for accurate distance calculations between coordinates.

### Error Handling
- API failures handled gracefully
- User-friendly error messages
- Input validation on all forms
- Fallback values for edge cases

## 🔧 Configuration

### Constants (config.py)
- MAX_ATTRACTION_DISTANCE_KM = 45
- ATTRACTION_IMAGE_SIZE = 1800
- CACHE_TTL_COORDINATES = 604800 (7 days)
- CACHE_TTL_ATTRACTIONS = 86400 (24 hours)

### Environment Variables
Copy .env.example to .env and configure:
\\\env
GROQ_API_KEY=your_key_here
\\\

## 📊 Testing Coverage

- ✅ Pricing calculations
- ✅ Distance calculations
- ✅ Input validation
- ✅ Error handling
- ✅ Coordinate validation

Target: >80% code coverage

## 🐛 Known Issues & Limitations

1. **Hotel Data**: Currently uses hardcoded hotel data. Real API integration planned.
2. **GPS Accuracy**: Browser geolocation accuracy varies by device/browser.
3. **API Rate Limits**: Wikipedia API has rate limits; caching mitigates this.

## 🚀 Deployment

### Streamlit Cloud
1. Connect GitHub repository
2. Set main file: pp.py
3. Add secrets in Streamlit Cloud dashboard
4. Deploy!

Live at: [https://detour.streamlit.app/](https://detour.streamlit.app/)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: git checkout -b feature/amazing-feature
3. Commit changes: git commit -m 'Add amazing feature'
4. Push to branch: git push origin feature/amazing-feature
5. Open Pull Request

## 📝 License

MIT License - feel free to use this project for learning and personal projects.

## 👨‍💻 Author

**Paula Martya**
- GitHub: [@paulamartya25](https://github.com/paulamartya25)
- Project: [detour_maniac.ai](https://github.com/paulamartya25/detour_maniac.ai)

## 🙏 Acknowledgments

- Wikipedia API for attraction data
- OpenStreetMap Nominatim for geocoding
- Streamlit for the amazing framework
- All contributors and users

---

**Made with ❤️ for travelers worldwide**
