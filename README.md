# 🤖 Tanzania Location-Based Service Search Chatbot

A conversational chatbot that helps users in Tanzania (especially Dar es Salaam) find nearby service providers using real OpenStreetMap data. Features budget-aware recommendations and WhatsApp-friendly interactions.

## ✨ Features

### 🗺️ OpenStreetMap Integration
- Real location data from OpenStreetMap for Tanzania
- Geocoding for Dar es Salaam and major Tanzanian cities
- Dynamic service provider discovery using Overpass API
- Accurate distance calculations with real map data

### 🏙️ Tanzania-Focused
- Pre-configured for Dar es Salaam districts and landmarks
- Support for major Tanzanian cities (Dodoma, Mwanza, Arusha, etc.)
- Tanzanian Shilling pricing with USD conversion
- Local landmarks and transportation information

### 💰 Budget-Aware Recommendations
- Filters by price range in Tanzanian Shillings (TZS)
- Low-cost: Under 50,000 TZS (~$20 USD)
- Mid-range: 50,000-150,000 TZS (~$20-65 USD)
- Premium: Over 150,000 TZS (~$65 USD)

### 🔄 Flexible Choice & Comparison
- Compare options by price, distance, rating, and accessibility
- Suggest alternatives when exact matches aren't found
- Interactive selection of preferred options

### 🚶 Accessibility & Directions
- Indicates walking distance, public transport, or vehicle requirements
- Provides location details and operating hours
- Clear accessibility guidance

### 💬 Conversational Interface
- WhatsApp-friendly short messages
- One question at a time approach
- Confirms preferences before final recommendations

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Internet connection for OpenStreetMap API access
- Ghala account for WhatsApp integration (optional)

### Installation
```bash
# Create virtual environment (recommended)
python3 -m venv tanzania_chatbot_env
source tanzania_chatbot_env/bin/activate  # Linux/Mac
# or
tanzania_chatbot_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment (interactive)
python setup_environment.py

# Run in console mode
python main.py

# Or run WhatsApp server
python main.py --whatsapp
```

### Quick Run Scripts
```bash
# Console mode
./run_chatbot.sh

# WhatsApp mode
./run_whatsapp.sh
```

### Dependencies
- `requests`: For OpenStreetMap and Ghala API calls
- `geopy`: For geocoding and distance calculations
- `overpy`: For OpenStreetMap Overpass API queries
- `flask`: Web framework for WhatsApp webhook handling
- `python-dotenv`: Environment variable management

### Usage
```bash
python main.py
```

Follow the conversational prompts:
1. Share your location (town, landmark, or GPS)
2. Specify the service you need
3. Set your budget range (optional)
4. Review and compare options
5. Get detailed information and directions

## 📋 Supported Services

- **Auto Repair**: Car maintenance and repair shops (karakana)
- **Medical**: Clinics and healthcare providers (hospitali, kliniki)
- **Hair Salon**: Haircuts and styling services (kinyozi, saluni)
- **Restaurant**: Food and dining options (migahawa, hoteli)
- **Plumbing**: Plumbing services (fundi bomba)
- **Electrical**: Electrical work (fundi umeme)
- **Cleaning**: Cleaning services (usafishaji)
- **Tutoring**: Educational services (kufundisha)
- **Extensible**: Easy to add new service types from OpenStreetMap data

## 🏗️ Architecture

### Core Components

#### `LocationBasedChatbot` Class
Main chatbot controller with state management and conversation flow.

#### `ServiceProvider` Dataclass
Represents service providers with location, pricing, and contact information.

#### `Location` Dataclass
Handles geographic coordinates and location metadata.

#### Conversation States
- `WELCOME`: Initial greeting
- `ASK_LOCATION`: Request user location
- `ASK_SERVICE`: Get service type
- `ASK_BUDGET`: Get budget preferences
- `SHOW_RESULTS`: Display search results
- `COMPARE_OPTIONS`: Compare multiple providers
- `GET_MORE_DETAILS`: Show detailed provider info
- `CONFIRM_CHOICE`: Final selection confirmation

## 🔧 Customization

### Adding New Service Providers
Edit the `_load_providers_database()` method in `main.py`:

```python
ServiceProvider(
    id="new_id",
    name="Provider Name",
    service_type="service_category",
    location=Location(lat, lon, "Area", "Landmark"),
    price_range=(min_price, max_price),
    rating=4.5,
    description="Service description",
    accessibility="walking",  # walking/public_transport/vehicle
    contact_info="+1-555-XXXX",
    operating_hours="Mon-Fri 9AM-6PM"
)
```

### Adding New Service Types
1. Add providers with the new service type
2. Update the service mapping in `_handle_service_input()`
3. Add appropriate keywords for recognition

### Location Enhancement
For production use, integrate with geocoding services:
- Google Maps Geocoding API
- OpenStreetMap Nominatim
- Mapbox Geocoding

## 📱 Integration Options

### WhatsApp Business API (Meta)
✅ **Implemented** - Full WhatsApp integration using Meta WhatsApp Business API

**Features:**
- ✅ **Text Messages**: Full conversational AI with Tanzania context
- ✅ **Location Sharing**: Automatic GPS coordinate processing from users
- ✅ **Location Messages**: Send service provider locations with map pins
- ✅ **Clickable Maps**: Google Maps links for directions and navigation
- ✅ **Real-time Responses**: Instant service recommendations from OpenStreetMap
- ✅ **Tanzania Optimized**: Local language and TZS currency support
- ✅ **Multi-user**: Handles multiple conversations simultaneously
- ✅ **Unicode Support**: Full emoji and Swahili character support

### WhatsApp Business API (Ghala)
✅ **Implemented** - Tanzania-focused WhatsApp integration using Ghala API

**Features:**
- ✅ **Ghala SDK**: Official SDK wrapper for easy integration
- ✅ **Template Messages**: Send approved message templates
- ✅ **Location Messages**: Send service locations with pins
- ✅ **Text Messages**: Simple text messaging
- ✅ **Tanzania Optimized**: Local infrastructure and pricing
- ✅ **Professional Templates**: Pre-built service recommendation templates

**Setup:**
```bash
# Interactive setup (recommended)
python setup_environment.py

# Or set manually
export WHATSAPP_PROVIDER='ghala'
export GHALA_APP_ID='your_ghala_app_id'
export GHALA_APP_SECRET='your_ghala_app_secret'

# Run with Ghala SDK
python example_ghala_usage.py

# Or run WhatsApp server
./run_whatsapp.sh
```

**Or Meta WhatsApp:**
```bash
# Interactive setup (recommended)
python setup_environment.py

# Or set manually
export WHATSAPP_PROVIDER='meta'
export WHATSAPP_ACCESS_TOKEN='your_access_token'
export WHATSAPP_PHONE_NUMBER_ID='your_phone_number_id'
export WHATSAPP_WABA_ID='your_waba_id'
export WHATSAPP_WEBHOOK_TOKEN='tanzania_service_bot'

# Run WhatsApp server
./run_whatsapp.sh
```

### Telegram Bot
Use python-telegram-bot library for Telegram integration.

### Web Interface
Add Flask/FastAPI backend with HTML frontend.

### SMS Integration
Use Twilio for SMS-based interactions or Ghala SMS API.

## 🧪 Testing

### Sample Conversations

**Basic Search:**
```
Bot: Hi! I'm your location-based service finder. What's your location?
User: Manhattan, near Times Square
Bot: What service are you looking for?
User: auto repair
Bot: What's your budget range?
User: under $100
Bot: [Shows filtered results with prices, distances, and details]
```

**Comparison:**
```
User: compare
Bot: [Shows side-by-side comparison of top options]
User: 2
Bot: [Shows detailed information for option 2]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your enhancements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 🔮 Future Enhancements

- Real geocoding API integration
- User reviews and ratings system
- Appointment booking functionality
- Multi-language support
- Real-time availability checking
- Integration with popular mapping services
- Voice message support
- Image-based location sharing

## 📞 Support

For questions or issues:
- Check the conversation flow in `main.py`
- Review the sample interactions above
- Ensure Python 3.7+ is installed

---

Built with ❤️ for accessible, location-aware service discovery.
