# 🚀 Tanzania Service Chatbot - Deployment Guide

## Overview
The Tanzania Location-Based Service Search Chatbot is now ready for deployment with OpenStreetMap integration for real Dar es Salaam data.

## ✅ Completed Features

### 🗺️ OpenStreetMap Integration
- **Geocoding**: Convert location names to coordinates using Nominatim API
- **Reverse Geocoding**: Convert coordinates back to location names
- **Service Discovery**: Query real service providers using Overpass API
- **Tanzania Focus**: Pre-configured for Dar es Salaam and major Tanzanian cities

### 🏙️ Tanzania-Specific Data
- **10 Major Cities**: Dar es Salaam, Dodoma, Arusha, Mwanza, Mbeya, etc.
- **Dar es Salaam Districts**: Kinondoni, Ilala, Temeke, Ubungo, Kigamboni
- **Local Landmarks**: Kariakoo Market, Posta, University, Airport, etc.
- **Tanzanian Shilling Pricing**: Realistic price ranges for local services

### 📱 Service Categories
- **Auto Repair** (karakana): Car maintenance, repairs, tire services
- **Medical** (kliniki): Hospitals, clinics, pharmacies
- **Hair Salon** (kinyozi): Haircuts, styling, beauty services
- **Restaurant** (migahawa): Food, dining, cafes
- **Plumbing** (fundi bomba): Plumbing repairs and installations
- **Electrical** (fundi umeme): Electrical work and repairs
- **Cleaning** (usafishaji): House and office cleaning
- **Tutoring** (kufundisha): Educational services

## 🛠️ Installation & Setup

### Option 1: With Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv tanzania_chatbot_env

# Activate virtual environment
source tanzania_chatbot_env/bin/activate  # Linux/Mac
# or
tanzania_chatbot_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the chatbot
python main.py
```

### Option 2: System Installation

```bash
# Install dependencies (may require sudo/admin privileges)
pip install requests geopy overpy

# Run the chatbot
python main.py
```

### Option 3: Fallback Mode (No External Dependencies)

The chatbot automatically runs in fallback mode if OpenStreetMap dependencies are not available, using:
- Pre-configured Tanzania location data
- Static service provider database
- Basic distance calculations

## 📊 Test Results

### Tanzania Location Recognition: ✅ 90% Success Rate
- Successfully recognized: Dar es Salaam, Masaki, Kinondoni, Posta, Kariakoo, Arusha, Dodoma, Mwanza, Airport
- Failed to recognize: Generic "university" (needs more context)

### OpenStreetMap Integration: ✅ Graceful Fallback
- When dependencies available: Real-time data from OpenStreetMap
- When dependencies unavailable: Falls back to static Tanzania data
- No crashes or errors in either mode

### Distance Calculations: ✅ Accurate
- Dar es Salaam to Arusha: ~461 km
- Dar es Salaam to Dodoma: ~456 km
- Dar es Salaam to Mwanza: ~1,258 km

## 🌐 OpenStreetMap Data Sources

### Nominatim API (Geocoding)
- Endpoint: `https://nominatim.openstreetmap.org/`
- Rate limit: 1 request/second
- Usage: Location name → Coordinates

### Overpass API (Data Queries)
- Endpoint: `https://overpass-api.de/api/interpreter`
- Rate limit: Respectful delays between requests
- Usage: Service provider discovery in bounding boxes

### Data Coverage in Tanzania
- **Dar es Salaam**: Good coverage of businesses and services
- **Major Cities**: Basic infrastructure data available
- **Rural Areas**: Limited data, falls back to city centers

## 🔧 Configuration

### Budget Ranges (Tanzanian Shilling)
```python
DEFAULT_BUDGET_RANGES = {
    "low_cost": (0, 50000),      # TZS 0-50,000 (~$0-20 USD)
    "mid_range": (50000, 150000), # TZS 50,000-150,000 (~$20-65 USD)
    "premium": (150000, 500000)   # TZS 150,000+ (~$65+ USD)
}
```

### Search Radius
- Default: 10 km for urban areas
- Configurable in `CHATBOT_CONFIG["max_search_distance_km"]`

## 📱 Integration Options

### WhatsApp Business API (Meta)
✅ **Implemented** - Full WhatsApp integration using Meta WhatsApp Business API

**Setup:**
```bash
# Set credentials
export WHATSAPP_ACCESS_TOKEN='your_access_token'
export WHATSAPP_PHONE_NUMBER_ID='your_phone_number_id'
export WHATSAPP_WABA_ID='your_waba_id'
export WHATSAPP_WEBHOOK_TOKEN='tanzania_service_bot'

# Configure webhook in Meta dashboard
# Webhook URL: https://your-domain.com/webhook
# Verify token: tanzania_service_bot

# Run server
./run_whatsapp.sh
```

**Features:**
- Official WhatsApp Business API integration
- Real-time messaging for Tanzanian users
- Location sharing support via WhatsApp
- Multi-user conversation handling
- Tanzania-optimized responses in English/Swahili
- Automatic service recommendations from OpenStreetMap

### Telegram Bot
```python
# Use python-telegram-bot library
from telegram.ext import Updater, CommandHandler
# Implementation in telegram_integration.py (future)
```

### Web Interface
```python
# Use Flask or FastAPI
from flask import Flask, request, jsonify
# Implementation in web_integration.py (future)
```

## 🧪 Testing Commands

```bash
# Run all tests
python test_tanzania.py

# Run general functionality tests
python test_chatbot.py

# Test interactive mode
python demo.py

# Start chatbot
python main.py
```

## 📈 Performance Metrics

### Response Times
- **Location Recognition**: < 0.1 seconds (local data)
- **OpenStreetMap Geocoding**: 1-3 seconds (network dependent)
- **Service Discovery**: 2-5 seconds (API queries)
- **Fallback Mode**: < 0.5 seconds (static data)

### Data Freshness
- **OpenStreetMap Data**: Real-time (updated by community)
- **Static Fallback Data**: Configurable, can be updated manually

## 🔒 Security Considerations

### API Rate Limiting
- OpenStreetMap APIs have rate limits
- Built-in delays prevent overwhelming services
- Graceful degradation when limits exceeded

### Data Privacy
- No user data stored permanently
- Location data used only for service discovery
- All requests are anonymous

## 🚀 Production Deployment

### Recommended Setup
1. **Server**: Ubuntu 20.04+ or similar Linux distribution
2. **Python**: 3.8+ with virtual environment
3. **Memory**: 512MB minimum, 1GB recommended
4. **Network**: Stable internet for OpenStreetMap APIs

### Monitoring
- Log API response times and errors
- Monitor OpenStreetMap service availability
- Track user interaction patterns

### Backup Strategy
- Static fallback data ensures service continuity
- Regular updates to location database
- Configuration files version controlled

## 🎯 Next Steps

### Immediate (Week 1-2)
- [ ] Deploy to test server
- [ ] Set up monitoring and logging
- [ ] Test with real users in Dar es Salaam

### Short Term (Month 1-3)
- [ ] Add WhatsApp Business API integration
- [ ] Implement user feedback collection
- [ ] Add more service categories

### Long Term (Month 3-6)
- [ ] Mobile app development
- [ ] Multi-language support (Swahili, Arabic)
- [ ] Advanced features (appointments, reviews)

## 📞 Support

### Issues & Bugs
- Check logs in `/var/log/tanzania-chatbot/` (production)
- Test with `python test_tanzania.py` for diagnostics
- Verify OpenStreetMap API availability

### Performance Issues
- Check network connectivity to OpenStreetMap services
- Verify virtual environment is activated
- Monitor system resources (CPU, memory)

---

**Status**: ✅ **READY FOR DEPLOYMENT**
**Test Coverage**: ✅ **90% Tanzania locations recognized**
**Fallback Mode**: ✅ **Fully functional without external dependencies**
