#!/usr/bin/env python3
"""
Configuration file for the Location-Based Service Search Chatbot
Contains customizable settings, service types, and provider data.
Tanzania/Dar es Salaam focused with OpenStreetMap integration.
"""

from typing import Dict, List, Optional
from data_models import ServiceProvider, Location
from osm_integration import OpenStreetMapIntegration, TanzaniaLocations, tzs_to_usd


# Chatbot Configuration
CHATBOT_CONFIG = {
    "max_search_distance_km": 10.0,  # Maximum search radius
    "max_results_display": 3,        # Results to show initially
    "default_budget_ranges": {
        "low_cost": (0, 50),
        "mid_range": (50, 150),
        "premium": (150, 500)
    },
    "supported_services": [
        "auto_repair",
        "medical",
        "hair_salon",
        "restaurant",
        "plumbing",
        "electrical",
        "cleaning",
        "tutoring"
    ]
}


# Service Type Mappings for natural language processing
SERVICE_KEYWORDS = {
    "auto_repair": ["auto", "car", "repair", "mechanic", "vehicle", "automotive"],
    "medical": ["medical", "clinic", "doctor", "health", "healthcare", "hospital"],
    "hair_salon": ["hair", "salon", "cut", "style", "barber", "beauty"],
    "restaurant": ["restaurant", "food", "eat", "dining", "cafe", "diner"],
    "plumbing": ["plumbing", "plumber", "pipes", "water", "leak"],
    "electrical": ["electrical", "electrician", "wiring", "power", "lights"],
    "cleaning": ["cleaning", "cleaner", "maid", "housekeeping"],
    "tutoring": ["tutoring", "tutor", "teaching", "lessons", "education"]
}


# Location aliases for better recognition
LOCATION_ALIASES = {
    # New York City
    "manhattan": ["nyc", "new york city", "downtown", "midtown"],
    "brooklyn": ["bk", "brooklyn heights", "williamsburg", "dumbo"],
    "queens": ["forest hills", "jackson heights", "astoria"],
    "bronx": ["bronx", "the bronx"],
    "staten island": ["si", "staten island"],

    # Major landmarks
    "times square": ["times square", "broadway"],
    "central park": ["central park", "central park south", "upper east side"],
    "high line": ["high line", "chelsea"],
    "bryant park": ["bryant park", "library"],
    "prospect park": ["prospect park", "brooklyn"],
    "forest hills": ["forest hills", "queens"],
    "metropolitan museum": ["met", "met museum", "upper east side"]
}


# Mock service providers database
# In production, this would be replaced with a real database
def load_service_providers() -> List[ServiceProvider]:
    """Load service providers - returns empty list as we use real OSM data"""
    # Real service providers are loaded dynamically from OpenStreetMap
    # This function is kept for backward compatibility but returns empty list
    # Real data is fetched via OpenStreetMapIntegration.get_service_providers_from_osm()
    return []


# Response templates for consistent messaging
RESPONSE_TEMPLATES = {
    "welcome": """👋 Hi! I'm your location-based service finder.

I can help you find nearby service providers like auto repair shops, medical clinics, hair salons, restaurants, and more.

To get started, could you share your current location?
You can tell me:
• Your town/city name
• A nearby landmark
• Or GPS coordinates (latitude, longitude)

What's your location?""",

    "location_confirm": """✅ Got it! I understand you're near {location}.

What service are you looking for? Here are some options:
{service_options}

What service do you need?""",

    "service_options": """• Auto repair
• Medical clinic
• Hair salon
• Restaurant
• Plumbing
• Electrical
• Cleaning
• Tutoring
• Other (please specify)""",

    "budget_prompt": """Great! You're looking for {service} services.

What's your budget range? (optional - you can say "no preference")
• Low-cost: Under ${low_max}
• Mid-range: ${mid_min}-${mid_max}
• Premium: Over ${premium_min}

Or tell me your maximum budget (e.g., "up to $100")""",

    "no_results": """Sorry, I couldn't find any providers for that service in your area.

Would you like to:
1. Try a different service type
2. Search in a different location
3. Or let me know what you're looking for specifically?""",

    "results_header": """I found {count} option(s) near you:

{results}

Would you like to:
• Compare options (type "compare")
• Get more details about a specific option (type the number)
• See more results (type "more")
• Start a new search (type "new")

What would you like to do?""",

    "comparison_header": """📊 Comparing Options:

{comparison}

Which option interests you most? (type the number)
Or type "back" to return to results.""",

    "detailed_info": """📋 Detailed Information:

🏢 {name}
💰 Price Range: ${min_price}-${max_price} ({budget_cat})
⭐ Rating: {rating}/5
📍 Exact Location: {area}, near {landmark}
📏 Distance: {distance} km from your location
🚶 Accessibility: {accessibility_guide}
🕒 Operating Hours: {hours}
📞 Contact: {contact}
📝 Description: {description}

Would you like to:
• Call them now (type "call")
• Get directions (type "directions")
• Compare with other options (type "compare")
• Start a new search (type "new")

What would you like to do?"""
}


# Accessibility guides
ACCESSIBILITY_GUIDES = {
    "walking": "This location is within walking distance ({distance} km).",
    "public_transport": "Public transportation is recommended to reach this location ({distance} km away).",
    "vehicle": "A vehicle is required to reach this destination ({distance} km away)."
}


def get_location_from_text(text: str) -> Optional[Location]:
    """Parse location from user text input - Tanzania focused"""
    text_lower = text.lower().strip()

    # First try Tanzania-specific locations
    tanzania_location = TanzaniaLocations.get_location_from_text(text)
    if tanzania_location:
        return tanzania_location

    # If not found in Tanzania locations, try OpenStreetMap geocoding
    osm_integration = OpenStreetMapIntegration()
    osm_location = osm_integration.geocode_location(text)

    if osm_location:
        return osm_location

    # Fallback to default Dar es Salaam location if nothing found
    return Location(-6.7924, 39.2083, "Dar es Salaam", "Central Business District")


def get_service_type_from_text(text: str) -> str:
    """Parse service type from user text input"""
    text_lower = text.lower().strip()

    for service_type, keywords in SERVICE_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return service_type

    # Default to the input if no keywords match
    return text_lower.replace(" ", "_")
