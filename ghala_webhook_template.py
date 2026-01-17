#!/usr/bin/env python3
"""
Ghala WhatsApp Webhook Template
Ready-to-use template for Ghala WhatsApp Business API integration
"""

from flask import Flask, request, jsonify
import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ===== CONFIGURATION =====
# Replace these with your actual Ghala credentials
GHALA_APP_ID = "your_ghala_app_id_here"
GHALA_APP_SECRET = "your_ghala_app_secret_here"
WEBHOOK_VERIFY_TOKEN = "tanzania_service_bot_verify_token"

# ===== GHALA API CONFIG =====
GHALA_BASE_URL = "https://dev.ghala.io/api/v1"
SEND_MESSAGE_URL = f"{GHALA_BASE_URL}/messages"

# ===== WEBHOOK VERIFICATION =====
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """
    Ghala webhook verification endpoint
    Add this URL to your Ghala dashboard: https://your-domain.com/webhook
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == WEBHOOK_VERIFY_TOKEN:
        logger.info("✅ Ghala webhook verified successfully")
        return challenge, 200
    else:
        logger.warning("❌ Ghala webhook verification failed")
        return 'Verification failed', 403

# ===== MESSAGE HANDLING =====
@app.route('/webhook', methods=['POST'])
def handle_message():
    """
    Handle incoming WhatsApp messages from Ghala
    """
    try:
        data = request.get_json()
        logger.info(f"📨 Received Ghala webhook: {data}")

        if data and 'messages' in data:
            for message in data['messages']:
                process_whatsapp_message(message)

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        logger.error(f"❌ Error handling Ghala webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def process_whatsapp_message(message):
    """
    Process individual WhatsApp messages from Ghala
    """
    try:
        message_type = message.get('type')
        sender_id = message.get('from')
        message_id = message.get('id')

        logger.info(f"💬 Processing {message_type} from {sender_id}")

        if message_type == 'text':
            text_content = message.get('text', {}).get('body', '')
            handle_text_message(sender_id, text_content)

        elif message_type == 'location':
            location_data = message.get('location', {})
            handle_location_message(sender_id, location_data)

        else:
            # Handle other message types
            send_whatsapp_message(
                sender_id,
                "👋 Hi! I can help you find services in Tanzania. Please send me a text message or share your location! 🗺️"
            )

    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")

# ===== MESSAGE HANDLERS =====
def handle_text_message(sender_id: str, text: str):
    """
    Handle text messages and generate responses
    """
    text_lower = text.lower().strip()

    # Simple response logic (replace with your chatbot logic)
    if 'hi' in text_lower or 'hello' in text_lower or 'habari' in text_lower:
        response = """🇹🇿 *Tanzania Service Finder*

Habari! I'm your AI assistant for finding services in Tanzania.

I can help you find:
🏪 *Auto repair* (karakana)
🏥 *Medical clinics* (kliniki)
✂️ *Hair salons* (kinyozi)
🍽️ *Restaurants* (migahawa)

Send me your location or tell me what you need! 📍"""

    elif 'location' in text_lower or 'restaurant' in text_lower or 'hotel' in text_lower:
        response = """🍽️ *Restaurant Search in Dar es Salaam*

Here are some popular restaurants:

🏪 *Beach Banda*
📍 Masaki Area
💰 TZS 15,000 - 45,000
⭐ Rating: 4.2/5

🏪 *The Terrace*
📍 Masaki Area
💰 TZS 25,000 - 60,000
⭐ Rating: 4.5/5

Would you like directions to any of these? Just reply with the name! 🗺️"""

    elif 'directions' in text_lower or 'map' in text_lower:
        response = """🗺️ *Directions in Dar es Salaam*

To get directions, I can send you:

1. 📍 *Location pins* - Tap to open in WhatsApp Maps
2. 🗺️ *Google Maps links* - For detailed navigation

Example: "directions to Beach Banda"

Share your location first, then ask for directions! 📍"""

    else:
        response = f"""🤔 I didn't understand: "{text}"

🇹🇿 *Try these commands:*
• "restaurants" - Find places to eat
• "medical" - Find clinics and hospitals
• "hair salon" - Find beauty services
• "directions" - Get navigation help

Or just share your location and ask what you need! 📍"""

    send_whatsapp_message(sender_id, response)

def handle_location_message(sender_id: str, location_data: dict):
    """
    Handle location sharing from users
    """
    try:
        latitude = location_data.get('latitude')
        longitude = location_data.get('longitude')

        if latitude and longitude:
            response = f"""📍 *Location Received!*

📌 Coordinates: {latitude}, {longitude}
🏙️ *Area: Dar es Salaam*

What service are you looking for near this location?

• 🍽️ Restaurants
• 🏥 Medical clinics
• ✂️ Hair salons
• 🚗 Auto repair

Just reply with what you need! 🤖"""

            send_whatsapp_message(sender_id, response)
        else:
            send_whatsapp_message(
                sender_id,
                "📍 Sorry, I couldn't read the location data. Please try sharing your location again! 🗺️"
            )

    except Exception as e:
        logger.error(f"❌ Error handling location: {e}")
        send_whatsapp_message(
            sender_id,
            "📍 Sorry, there was an error processing your location. Please try again! 🗺️"
        )

# ===== SEND MESSAGES =====
def send_whatsapp_message(recipient_id: str, message: str):
    """
    Send message via Ghala WhatsApp API

    Ghala API Format:
    POST https://dev.ghala.io/api/v1/messages
    Headers:
      Authorization: Bearer {APP_SECRET}
      Content-Type: application/json
      X-App-Id: {APP_ID}
    Body:
      {
        "to": "recipient_phone_number",
        "type": "text",
        "text": {"body": "message_content"}
      }
    """
    try:
        if not GHALA_APP_ID or not GHALA_APP_SECRET:
            logger.error("❌ Ghala credentials not configured")
            return False

        payload = {
            "to": recipient_id,
            "type": "text",
            "text": {
                "body": message
            }
        }

        headers = {
            "Authorization": f"Bearer {GHALA_APP_SECRET}",
            "Content-Type": "application/json",
            "X-App-Id": GHALA_APP_ID
        }

        logger.info(f"📤 Sending message to {recipient_id}")
        response = requests.post(
            SEND_MESSAGE_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            logger.info(f"✅ Message sent successfully to {recipient_id}")
            return True
        else:
            logger.error(f"❌ Failed to send message: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ Error sending message: {e}")
        return False

# ===== LOCATION MESSAGES =====
def send_location_message(recipient_id: str, latitude: float, longitude: float,
                         name: str = None, address: str = None):
    """
    Send location message via Ghala WhatsApp API

    Ghala Location API Format:
    POST https://dev.ghala.io/api/v1/messages
    Headers:
      Authorization: Bearer {APP_SECRET}
      Content-Type: application/json
      X-App-Id: {APP_ID}
    Body:
      {
        "to": "recipient_phone_number",
        "type": "location",
        "location": {
          "latitude": "latitude_value",
          "longitude": "longitude_value",
          "name": "location_name",
          "address": "location_address"
        }
      }
    """
    try:
        if not GHALA_APP_ID or not GHALA_APP_SECRET:
            logger.error("❌ Ghala credentials not configured")
            return False

        payload = {
            "to": recipient_id,
            "type": "location",
            "location": {
                "latitude": str(latitude),
                "longitude": str(longitude)
            }
        }

        # Add optional fields
        if name:
            payload["location"]["name"] = name
        if address:
            payload["location"]["address"] = address

        headers = {
            "Authorization": f"Bearer {GHALA_APP_SECRET}",
            "Content-Type": "application/json",
            "X-App-Id": GHALA_APP_ID
        }

        logger.info(f"📍 Sending location to {recipient_id}: {latitude}, {longitude}")
        response = requests.post(
            SEND_MESSAGE_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            logger.info(f"✅ Location sent successfully to {recipient_id}")

            # Also send Google Maps link
            maps_link = f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}"
            text_message = f"""🗺️ *Location sent above!* 📍

🗺️ *Google Maps Link:*
{maps_link}

Tap the location pin above or click the link for directions! 🚗"""

            send_whatsapp_message(recipient_id, text_message)
            return True
        else:
            logger.error(f"❌ Failed to send location: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ Error sending location: {e}")
        return False

# ===== HEALTH CHECK =====
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Ghala WhatsApp Tanzania Service Bot',
        'timestamp': datetime.now().isoformat(),
        'webhook_url': 'https://your-domain.com/webhook'
    })

# ===== MAIN =====
if __name__ == '__main__':
    print("🇹🇿 Ghala WhatsApp Tanzania Service Bot")
    print("=" * 50)
    print("📱 Webhook URL: https://your-domain.com/webhook")
    print("❤️  Health Check: http://localhost:5000/health")
    print("🔑 Configure these in your Ghala dashboard:")
    print(f"   • Webhook URL: https://your-domain.com/webhook")
    print(f"   • Verify Token: {WEBHOOK_VERIFY_TOKEN}")
    print()
    print("⚙️  Environment variables needed:")
    print(f"   export GHALA_APP_ID='{GHALA_APP_ID}'")
    print(f"   export GHALA_APP_SECRET='{GHALA_APP_SECRET}'")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5000, debug=True)
