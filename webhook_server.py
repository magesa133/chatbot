#!/usr/bin/env python3
"""
Standalone WhatsApp Webhook Server for Tanzania Service Chatbot
Handles both Ghala and Meta WhatsApp webhooks

🧪 TESTING CONFIGURATION WARNING:
This file contains test-specific code and configurations that should NOT be used in production:
- Hardcoded test phone numbers
- Simplified security measures
- Test environment responses

For production deployment:
1. Remove test phone number validations
2. Implement proper authentication
3. Add rate limiting and security measures
4. Use production-grade responses
5. Implement comprehensive logging

⚠️  SECURITY NOTICE: This is a development/testing environment only!
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for all origins (required for ngrok/webhook access)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-App-Id"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# ===== WEBHOOK ROUTES =====

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Verify webhook with WhatsApp provider (Meta or Ghala)
    This endpoint handles the initial webhook verification
    """
    from env_config import Config

    # Get the appropriate webhook token based on provider
    if Config.WHATSAPP_PROVIDER == 'meta':
        webhook_token = Config.WHATSAPP_WEBHOOK_TOKEN
    elif Config.WHATSAPP_PROVIDER == 'ghala':
        webhook_token = Config.GHALA_WEBHOOK_TOKEN
    else:
        webhook_token = 'tanzania_service_bot'

    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    logger.info(f"Webhook verification attempt - Mode: {mode}, Token: {token[:10]}...")

    if mode == 'subscribe' and token == webhook_token:
        logger.info("✅ Webhook verified successfully!")
        return challenge, 200
    else:
        logger.warning("❌ Webhook verification failed")
        return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def handle_message():
    """
    Handle incoming WhatsApp messages from both providers
    """
    try:
        data = request.get_json()
        logger.info(f"📨 Received webhook data from {request.remote_addr}")

        if not data:
            logger.warning("No data received")
            return jsonify({'status': 'error', 'message': 'No data'}), 400

        # Handle Meta WhatsApp format
        if 'object' in data and data['object'] == 'whatsapp_business_account':
            return handle_meta_whatsapp(data)

        # Handle Ghala WhatsApp format
        elif 'messages' in data:
            return handle_ghala_whatsapp(data)

        else:
            logger.warning(f"Unknown webhook format: {list(data.keys())}")
            return jsonify({'status': 'error', 'message': 'Unknown format'}), 400

    except Exception as e:
        logger.error(f"❌ Error handling webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def handle_directions_request(text):
    """
    Handle specific directions requests to named locations
    """
    text_lower = text.lower()

    # Restaurant directions
    if 'beach banda' in text_lower:
        return """🗺️ *Directions to Beach Banda Restaurant*

📍 *Location:* Oyster Bay, Masaki Area, Dar es Salaam
🗺️ *Coordinates:* -6.7924, 39.2727 (approx.)
🚗 *Address:* Masaki Peninsula Road, Oyster Bay

🛣️ *Getting There:*

🚕 *By Taxi/Boda Boda:*
• From City Center: ~15-20 minutes
• Cost: TZS 5,000-8,000
• Look for the blue building with ocean views

🚌 *By Public Transport:*
• Take daladala route 23 or 24 to Masaki
• Get off at Oyster Bay stop
• Walk 200m towards the beach

🕐 *Business Hours:* 11:00 AM - 11:00 PM
☎️ *Contact:* Call ahead for reservations

💡 *Navigation Tip:* The restaurant is right on the beach with excellent ocean views. Parking available on-site.

Would you like me to help you with anything else? 🍽️"""

    elif 'terrace' in text_lower:
        return """🗺️ *Directions to The Terrace Restaurant & Bar*

📍 *Location:* Masaki Peninsula, Dar es Salaam
🗺️ *Coordinates:* -6.7892, 39.2751 (approx.)
🚗 *Address:* The Kilimanjaro Hotel, Masaki

🛣️ *Getting There:*

🚕 *By Taxi/Boda Boda:*
• From City Center: ~12-18 minutes
• Cost: TZS 6,000-10,000
• Located in the Kilimanjaro Hotel complex

🚌 *By Public Transport:*
• Take daladala to Masaki roundabout
• Continue walking towards the peninsula
• Look for the hotel entrance

🕐 *Business Hours:* 12:00 PM - 12:00 AM
☎️ *Contact:* Part of Kilimanjaro Hotel - call hotel reception

💡 *Navigation Tip:* Elegant rooftop dining with panoramic views of the Indian Ocean. Valet parking available.

Would you like me to help you with anything else? 🥂"""

    # Medical facility directions
    elif 'aga khan' in text_lower or 'aga khan hospital' in text_lower:
        return """🗺️ *Directions to Aga Khan Hospital Dar es Salaam*

📍 *Location:* Ohio Street, City Center, Dar es Salaam
🗺️ *Coordinates:* -6.8167, 39.2892 (approx.)
🚗 *Address:* P.O. Box 2289, Dar es Salaam

🛣️ *Getting There:*

🚕 *By Taxi/Boda Boda:*
• Most accessible location in CBD
• Cost: TZS 2,000-5,000 from nearby areas
• Clearly marked hospital entrance

🚌 *By Public Transport:*
• Multiple daladala routes stop nearby
• Walking distance from most city center locations
• Well-known landmark in the business district

🚨 *Emergency Services:* 24/7 Emergency Department
☎️ *Contact:* +255 22 211 5151 (Main) / +255 22 211 5152 (Emergency)

💡 *Navigation Tip:* Large modern hospital with clear signage. Emergency entrance on the side street. Ample parking available.

For emergencies, proceed directly to the hospital. 🏥"""

    elif 'masaki medical' in text_lower:
        return """🗺️ *Directions to Masaki Medical Centre*

📍 *Location:* Masaki Area, Dar es Salaam
🗺️ *Coordinates:* -6.7901, 39.2738 (approx.)
🚗 *Address:* Masaki Commercial Area

🛣️ *Getting There:*

🚕 *By Taxi/Boda Boda:*
• From City Center: ~15-20 minutes
• Cost: TZS 5,000-8,000
• Look for the medical center signage

🚌 *By Public Transport:*
• Take daladala route 23 or 24 to Masaki
• Get off at Masaki commercial area
• Short walk to the medical center

🕐 *Business Hours:* 8:00 AM - 8:00 PM (Mon-Sat)
☎️ *Contact:* +255 XX XXX XXXX
🚨 *Emergency:* 24/7 services available

💡 *Navigation Tip:* Modern medical facility in the commercial area. Easy parking and clear signage.

Would you like me to help you with anything else? 🏥"""

    # Hair salon directions
    elif 'masaki hair' in text_lower:
        return """🗺️ *Directions to Masaki Hair Studio & Spa*

📍 *Location:* Masaki Area, Dar es Salaam
🗺️ *Coordinates:* -6.7915, 39.2742 (approx.)
🚗 *Address:* Masaki Shopping Center

🛣️ *Getting There:*

🚕 *By Taxi/Boda Boda:*
• From City Center: ~15-20 minutes
• Cost: TZS 5,000-8,000
• Located in Masaki shopping complex

🚌 *By Public Transport:*
• Take daladala to Masaki roundabout
• Walk to the shopping center
• Look for beauty salon signage

🕐 *Business Hours:* 10:00 AM - 8:00 PM (Mon-Sun)
☎️ *Contact:* +255 XX XXX XXXX (Call for appointment)

💡 *Navigation Tip:* Premium salon in upscale shopping area. Professional styling and spa services available.

Would you like me to help you with anything else? ✂️"""

    else:
        # Generic directions response for unrecognized places
        place_name = text.replace('directions to', '').strip()
        return f"""🗺️ *Directions Request for "{place_name}"*

I don't have specific directions for "{place_name}" in my database, but I can help you find similar services!

🇹🇿 *Try these options:*

🍽️ *For Restaurants:*
• "restaurants" - Browse dining options
• "directions to Beach Banda" - Popular seafood restaurant

🏥 *For Medical Services:*
• "medical clinics" - Find healthcare facilities
• "directions to Aga Khan Hospital" - Major hospital

✂️ *For Beauty Services:*
• "hair salons" - Find beauty salons
• "directions to Masaki Hair Studio" - Premium salon

💡 *Alternative:* Share your current location, and I'll recommend the best services near you!

What type of service are you looking for? 📍"""

def handle_meta_whatsapp(data):
    """
    Handle Meta WhatsApp webhook format
    """
    try:
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                if change.get('field') == 'messages':
                    messages = change.get('value', {}).get('messages', [])
                    contacts = change.get('value', {}).get('contacts', [])

                    for message in messages:
                        sender_id = message.get('from')
                        message_type = message.get('type')

                        logger.info(f"Meta WhatsApp - {message_type} from {sender_id}")

                        # 🔧 TESTING ONLY: Validate sender (basic security for test environment)
                        # ⚠️  WARNING: This is for testing purposes only!
                        # PRODUCTION SECURITY REQUIREMENTS:
                        # 1. Remove hardcoded phone numbers
                        # 2. Implement proper user authentication
                        # 3. Add rate limiting (max 1000 messages/hour per user)
                        # 4. Validate phone number ownership
                        # 5. Add spam protection
                        # 6. Log all interactions for audit purposes
                        test_senders = ['255612062161', '0612062161']  # TEST NUMBERS ONLY - REMOVE IN PRODUCTION
                        allowed_senders = test_senders + ['255XXXXXXXXX']  # Allow test numbers + demo

                        if sender_id not in allowed_senders:
                            logger.warning(f"🚫 Unauthorized sender blocked: {sender_id}")
                            logger.info("💡 Only test numbers are allowed in this demo environment")
                            # PRODUCTION: Return appropriate error response or ignore silently
                            return jsonify({'status': 'ignored', 'reason': 'test_environment'}), 200

                        logger.info(f"✅ Authorized test sender: {sender_id} (TEST ENVIRONMENT)")

                        if message_type == 'text':
                            text = message.get('text', {}).get('body', '')
                            response = process_message(text, sender_id)
                            send_meta_reply(sender_id, response)

                        elif message_type == 'location':
                            location = message.get('location', {})
                            response = f"📍 Location received: {location.get('latitude')}, {location.get('longitude')}"
                            send_meta_reply(sender_id, response)

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Error handling Meta WhatsApp: {e}")
        return jsonify({'status': 'error'}), 500

def handle_ghala_whatsapp(data):
    """
    Handle Ghala WhatsApp webhook format
    """
    try:
        for message in data.get('messages', []):
            sender_id = message.get('from')
            message_type = message.get('type')

            logger.info(f"Ghala WhatsApp - {message_type} from {sender_id}")

            if message_type == 'text':
                text = message.get('text', {}).get('body', '')
                response = process_message(text, sender_id)
                send_ghala_reply(sender_id, response)

            elif message_type == 'location':
                location = message.get('location', {})
                response = f"📍 Location received: {location.get('latitude')}, {location.get('longitude')}"
                send_ghala_reply(sender_id, response)

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"Error handling Ghala WhatsApp: {e}")
        return jsonify({'status': 'error'}), 500

def process_message(text, sender_id):
    """
    Process incoming message and generate response
    This is where you integrate with your chatbot logic
    """
    text = text.lower().strip()

    # Simple response logic (replace with your chatbot)
    if 'hi' in text or 'hello' in text or 'habari' in text:
        return """🇹🇿 *Tanzania Service Assistant*

Hello! Welcome to Tanzania's premier service discovery platform.

I can help you find trusted local services including:

🍽️ *Restaurants & Dining*
🏥 *Medical Clinics & Healthcare*
✂️ *Beauty Salons & Hair Services*
🏪 *Auto Repair & Maintenance*

💡 *How to use:*
• Type "restaurants" for dining options
• Type "medical clinics" for healthcare
• Type "hair salons" for beauty services
• Share your location for personalized recommendations

What service are you looking for today? 📍"""

    elif 'restaurant' in text or 'food' in text:
        return """🍽️ *Recommended Restaurants in Dar es Salaam*

Here are some highly-rated dining options in your area:

🥘 *Beach Banda Restaurant*
📍 Oyster Bay, Masaki Area
💰 Average meal: TZS 15,000-45,000
📏 Distance: ~2.3 km
⭐ Rating: 4.2/5 (Excellent seafood)
🕐 Open: 11:00 AM - 11:00 PM
☎️ Call: +255 XX XXX XXXX

🥂 *The Terrace Restaurant & Bar*
📍 Masaki Peninsula, Dar es Salaam
💰 Average meal: TZS 25,000-60,000
📏 Distance: ~1.8 km
⭐ Rating: 4.5/5 (Fine dining experience)
🕐 Open: 12:00 PM - 12:00 AM
☎️ Call: +255 XX XXX XXXX

🍲 *Addis Ababa Restaurant*
📍 Samora Avenue, City Center
💰 Average meal: TZS 12,000-35,000
📏 Distance: ~4.1 km
⭐ Rating: 4.0/5 (Ethiopian & International)
🕐 Open: 10:00 AM - 10:00 PM
☎️ Call: +255 XX XXX XXXX

💡 *To get directions:*
Reply with the restaurant name (e.g., "directions to Beach Banda")

Would you like me to show more options or help with reservations? 🗺️"""

    elif 'medical' in text or 'clinic' in text or 'hospital' in text or 'health' in text:
        return """🏥 *Healthcare Facilities in Dar es Salaam*

Here are reputable medical facilities in your area:

🏥 *Masaki Medical Centre*
📍 Masaki Area, Dar es Salaam
💰 Consultation: TZS 15,000-30,000
📏 Distance: ~2.1 km
⭐ Rating: 4.3/5 (General Practice)
🕐 Hours: 8:00 AM - 8:00 PM (Mon-Sat)
☎️ Emergency: +255 XX XXX XXXX (24/7)
🏥 Services: General medicine, pediatrics, diagnostics

🏥 *Aga Khan Hospital Dar es Salaam*
📍 Ohio Street, City Center
💰 Consultation: TZS 25,000-50,000
📏 Distance: ~3.8 km
⭐ Rating: 4.6/5 (Multi-specialty hospital)
🕐 Hours: 24/7 Emergency Services
☎️ Main: +255 XX XXX XXXX
🏥 Services: Complete medical care, surgery, maternity

🏥 *Muhimbili National Hospital*
📍 Upanga Area, Dar es Salaam
💰 Public rates (affordable care)
📏 Distance: ~5.2 km
⭐ Rating: 3.8/5 (National referral center)
🕐 Hours: 24/7 Emergency Services
☎️ Emergency: +255 XX XXX XXXX
🏥 Services: Full hospital services, specialist care

⚠️ *Emergency Services:*
For medical emergencies, call 112 or visit the nearest facility.

💡 *To get directions:*
Reply with the facility name (e.g., "directions to Aga Khan Hospital")

Do you need immediate assistance or appointment booking? 🗺️"""

    elif 'hair' in text or 'salon' in text or 'beauty' in text:
        return """✂️ *Beauty & Hair Salons in Dar es Salaam*

Here are professional beauty services in your area:

✂️ *Kinondoni Beauty Salon*
📍 Kinondoni Area, Dar es Salaam
💰 Services: TZS 5,000-25,000
📏 Distance: ~1.9 km
⭐ Rating: 4.1/5 (Local favorite)
🕐 Hours: 9:00 AM - 7:00 PM (Mon-Sat)
💇‍♀️ Services: Haircuts, styling, treatments, braiding
☎️ Call: +255 XX XXX XXXX

✂️ *Masaki Hair Studio & Spa*
📍 Masaki Area, Dar es Salaam
💰 Services: TZS 8,000-35,000
📏 Distance: ~2.4 km
⭐ Rating: 4.4/5 (Premium salon)
🕐 Hours: 10:00 AM - 8:00 PM (Mon-Sun)
💅 Services: Full beauty services, spa treatments
☎️ Call: +255 XX XXX XXXX

✂️ *City Center Cuts & Styles*
📍 Samora Avenue, CBD
💰 Services: TZS 3,000-15,000
📏 Distance: ~4.0 km
⭐ Rating: 3.9/5 (Affordable & quick)
🕐 Hours: 8:00 AM - 6:00 PM (Mon-Sat)
✂️ Services: Quick cuts, styling, men's grooming
☎️ Call: +255 XX XXX XXXX

💡 *To get directions:*
Reply with the salon name (e.g., "directions to Masaki Hair Studio")

Would you like to book an appointment or see more options? 🗺️"""

    elif 'directions to' in text.lower():
        # Handle specific directions requests
        return handle_directions_request(text)

    elif 'location' in text or 'directions' in text:
        return """🗺️ *Navigation & Directions Service*

I can provide detailed directions and location pins for any service in Dar es Salaam.

📋 *How to get directions:*

1️⃣ *Find a service first:*
• "restaurants" - Browse dining options
• "medical clinics" - Find healthcare facilities
• "hair salons" - Locate beauty services

2️⃣ *Request directions:*
• "directions to Beach Banda"
• "directions to Aga Khan Hospital"
• "directions to Masaki Hair Studio"

3️⃣ *Share your location:*
Send your current GPS location for personalized recommendations and accurate distances.

💡 *Example:*
User: "restaurants"
Bot: [Shows restaurant list]
User: "directions to Beach Banda"
Bot: [Sends location pin with navigation]

Would you like me to help you find a specific service first? 📍"""

    else:
        return f"""🤔 I didn't quite understand your request: "{text[:50]}..."

🇹🇿 *Tanzania Service Assistant - Available Commands:*

🍽️ *Dining & Restaurants*
• "restaurants" - Find places to eat
• "directions to [restaurant name]" - Get navigation

🏥 *Healthcare Services*
• "medical clinics" - Find healthcare facilities
• "directions to [clinic name]" - Get hospital/clinic directions

✂️ *Beauty & Personal Care*
• "hair salons" - Find beauty salons
• "directions to [salon name]" - Get salon directions

🗺️ *Navigation Help*
• Share your GPS location for personalized recommendations
• Use "directions to [place]" for any location

💡 *Pro Tips:*
• Be specific: "Italian restaurants" or "emergency clinics"
• Share location for accurate distances
• Use service names exactly as shown

How can I assist you with services in Tanzania today? 📍"""

def send_meta_reply(recipient_id, message):
    """
    Send reply via Meta WhatsApp API
    """
    from env_config import Config

    if not Config.WHATSAPP_ACCESS_TOKEN or not Config.WHATSAPP_PHONE_NUMBER_ID:
        logger.error("Meta WhatsApp credentials not configured")
        return False

    import requests

    url = f"https://graph.facebook.com/v18.0/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message}
    }

    headers = {
        "Authorization": f"Bearer {Config.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            logger.info(f"✅ Meta reply sent to {recipient_id}")
            return True
        else:
            logger.error(f"❌ Meta reply failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Meta reply error: {e}")
        return False

def send_ghala_reply(recipient_id, message):
    """
    Send reply via Ghala WhatsApp API
    """
    from env_config import Config

    if not Config.GHALA_APP_ID or not Config.GHALA_APP_SECRET:
        logger.error("Ghala credentials not configured")
        return False

    import requests

    url = "https://dev.ghala.io/api/v1/messages"

    payload = {
        "to": recipient_id,
        "type": "text",
        "text": {"body": message}
    }

    headers = {
        "Authorization": f"Bearer {Config.GHALA_APP_SECRET}",
        "Content-Type": "application/json",
        "X-App-Id": Config.GHALA_APP_ID
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            logger.info(f"✅ Ghala reply sent to {recipient_id}")
            return True
        else:
            logger.error(f"❌ Ghala reply failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Ghala reply error: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    from env_config import Config

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Tanzania Service Chatbot Webhook',
        'provider': Config.WHATSAPP_PROVIDER,
        'configured': Config.is_whatsapp_configured()
    })

@app.route('/', methods=['GET'])
def home():
    """Home page with webhook information"""
    from env_config import Config

    provider = Config.WHATSAPP_PROVIDER.upper() if Config.WHATSAPP_PROVIDER else 'UNKNOWN'

    return f"""
    <h1>🇹🇿 Tanzania Service Chatbot Webhook</h1>
    <h2>Provider: {provider}</h2>

    <h3>Webhook Endpoints:</h3>
    <ul>
        <li><strong>GET /webhook</strong> - Webhook verification</li>
        <li><strong>POST /webhook</strong> - Incoming WhatsApp messages</li>
        <li><strong>GET /health</strong> - Health check</li>
    </ul>

    <h3>Configuration Status:</h3>
    <ul>
        <li>Provider: {provider}</li>
        <li>Configured: {'✅ Yes' if Config.is_whatsapp_configured() else '❌ No'}</li>
    </ul>

    <h3>Setup Instructions:</h3>
    <ol>
        <li>Configure your webhook URL in your WhatsApp provider dashboard</li>
        <li>Set environment variables with your credentials</li>
        <li>Test with the /health endpoint</li>
        <li>Send test messages to your WhatsApp number</li>
    </ol>

    <p><strong>Need help?</strong> Check the setup guide or contact support.</p>
    """

# ===== MAIN =====
if __name__ == '__main__':
    from env_config import Config

    print("🇹🇿 Tanzania Service Chatbot Webhook Server")
    print("=" * 60)

    # Show configuration status
    print(f"📱 WhatsApp Provider: {Config.WHATSAPP_PROVIDER.upper()}")
    print(f"✅ Configured: {'Yes' if Config.is_whatsapp_configured() else 'No'}")

    if Config.is_whatsapp_configured():
        print("🎉 Ready to receive WhatsApp messages!")
    else:
        print("⚠️  WhatsApp not configured - set credentials first:")
        print("   Run: python setup_environment.py")
        print("   Or set environment variables manually")

    print()
    print("🌐 Webhook URLs:")
    print("   GET  /webhook  - Webhook verification")
    print("   POST /webhook  - Incoming messages")
    print("   GET  /health   - Health check")
    print("   GET  /         - This page")
    print()
    print("🚀 Starting server on http://0.0.0.0:5000")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=False)
