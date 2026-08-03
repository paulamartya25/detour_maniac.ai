"""Real hotel data for different cities in India."""

# Real hotel chains and properties mapped by city
REAL_HOTELS_BY_CITY = {
    "goa": [
        {"name": "Taj Exotica Resort & Spa Goa", "stars": 5, "area": "Benaulim"},
        {"name": "ITC Grand Goa Resort & Spa", "stars": 5, "area": "Arossim Beach"},
        {"name": "Park Hyatt Goa Resort and Spa", "stars": 5, "area": "Cansaulim"},
        {"name": "Novotel Goa Dona Sylvia Resort", "stars": 4, "area": "Cavelossim Beach"},
        {"name": "Holiday Inn Resort Goa", "stars": 4, "area": "Mobor Beach"},
        {"name": "Lemon Tree Hotel Candolim", "stars": 3, "area": "Candolim"},
        {"name": "Keys Select Ronil Resort", "stars": 3, "area": "Baga"},
        {"name": "FabHotel Prime Sea Pearl", "stars": 2, "area": "Calangute"},
        {"name": "Treebo Trend Palms Residency", "stars": 2, "area": "Panjim"},
    ],
    "mumbai": [
        {"name": "The Taj Mahal Palace Mumbai", "stars": 5, "area": "Colaba"},
        {"name": "The Oberoi Mumbai", "stars": 5, "area": "Nariman Point"},
        {"name": "JW Marriott Mumbai Sahar", "stars": 5, "area": "Andheri East"},
        {"name": "Hyatt Regency Mumbai", "stars": 4, "area": "Sahar"},
        {"name": "Novotel Mumbai Juhu Beach", "stars": 4, "area": "Juhu"},
        {"name": "Lemon Tree Premier Mumbai International Airport", "stars": 3, "area": "Andheri"},
        {"name": "Hotel Suba Palace", "stars": 3, "area": "Colaba"},
        {"name": "FabHotel Benz Suites Andheri", "stars": 2, "area": "Andheri West"},
        {"name": "Treebo Trend Olive Residency", "stars": 2, "area": "Vile Parle"},
    ],
    "delhi": [
        {"name": "The Leela Palace New Delhi", "stars": 5, "area": "Chanakyapuri"},
        {"name": "The Oberoi New Delhi", "stars": 5, "area": "Zakir Hussain Marg"},
        {"name": "ITC Maurya New Delhi", "stars": 5, "area": "Diplomatic Enclave"},
        {"name": "Hyatt Regency Delhi", "stars": 4, "area": "Bhikaji Cama Place"},
        {"name": "Radisson Blu Plaza Delhi Airport", "stars": 4, "area": "Mahipalpur"},
        {"name": "Lemon Tree Premier Delhi Airport", "stars": 3, "area": "Aerocity"},
        {"name": "Hotel Clark Greens", "stars": 3, "area": "Paharganj"},
        {"name": "FabHotel Prime Sai Residency", "stars": 2, "area": "Karol Bagh"},
        {"name": "Treebo Trend Green View", "stars": 2, "area": "New Delhi Railway Station"},
    ],
    "bangalore": [
        {"name": "Taj West End Bangalore", "stars": 5, "area": "Race Course Road"},
        {"name": "The Oberoi Bangalore", "stars": 5, "area": "MG Road"},
        {"name": "ITC Gardenia Bengaluru", "stars": 5, "area": "Residency Road"},
        {"name": "Hyatt Centric MG Road Bangalore", "stars": 4, "area": "MG Road"},
        {"name": "Radisson Blu Bengaluru Outer Ring Road", "stars": 4, "area": "Marathahalli"},
        {"name": "Lemon Tree Hotel Electronics City", "stars": 3, "area": "Electronic City"},
        {"name": "Keys Select Hotel Nestor", "stars": 3, "area": "Indiranagar"},
        {"name": "FabHotel Prime Royal Inn", "stars": 2, "area": "BTM Layout"},
        {"name": "Treebo Trend Cyan Suites", "stars": 2, "area": "Koramangala"},
    ],
    "jaipur": [
        {"name": "The Oberoi Rajvilas Jaipur", "stars": 5, "area": "Goner Road"},
        {"name": "Taj Jai Mahal Palace Jaipur", "stars": 5, "area": "Civil Lines"},
        {"name": "ITC Rajputana Jaipur", "stars": 5, "area": "Gopalbari"},
        {"name": "Hyatt Regency Jaipur Mansarovar", "stars": 4, "area": "Mansarovar"},
        {"name": "Radisson Jaipur City Center", "stars": 4, "area": "MI Road"},
        {"name": "Lemon Tree Premier Jaipur", "stars": 3, "area": "Tonk Road"},
        {"name": "Hotel Pearl Palace", "stars": 3, "area": "Gopal Bari"},
        {"name": "FabHotel Marigold Bani Park", "stars": 2, "area": "Bani Park"},
        {"name": "Treebo Trend Jaipur House", "stars": 2, "area": "Near Railway Station"},
    ],
}

# Default fallback hotels for cities not in database
DEFAULT_HOTELS = [
    {"name": "Taj Hotel", "stars": 5, "area": "City Center"},
    {"name": "ITC Grand", "stars": 5, "area": "Downtown"},
    {"name": "Hyatt Regency", "stars": 4, "area": "Business District"},
    {"name": "Radisson Blu", "stars": 4, "area": "Main Area"},
    {"name": "Lemon Tree Hotel", "stars": 3, "area": "Central"},
    {"name": "Keys Select", "stars": 3, "area": "City"},
    {"name": "FabHotel", "stars": 2, "area": "Near Station"},
    {"name": "Treebo Trend", "stars": 2, "area": "Market Area"},
]

def get_real_hotels(city: str, budget_range: tuple) -> list:
    '''Get real hotel names for a city filtered by budget.'''
    from utils.pricing import HotelPricingModel, HotelStarCategory

    city_key = city.lower().strip()

    # Get hotels for this city, or use defaults
    if city_key in REAL_HOTELS_BY_CITY:
        available_hotels = REAL_HOTELS_BY_CITY[city_key]
    else:
        # Use city name in default hotels
        available_hotels = [
            {
                'name': f"{h['name']} {city}",
                'stars': h['stars'],
                'area': h['area']
            }
            for h in DEFAULT_HOTELS
        ]

    # Filter by budget
    user_min, user_max = budget_range
    filtered = []

    for hotel in available_hotels:
        star_category = [cat for cat in HotelStarCategory if cat.value == hotel['stars']][0]
        price_range = HotelPricingModel.get_price_range(star_category)

        # Check if hotel price overlaps with user budget
        if price_range.min_price <= user_max and price_range.max_price >= user_min:
            filtered.append({
                'name': hotel['name'],
                'category': star_category,
                'area': hotel['area']
            })

    return filtered
