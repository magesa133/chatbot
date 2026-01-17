#!/usr/bin/env python3
"""
Simple Ghala WhatsApp Webhook Template
Copy this code directly into Ghala platform webhook configuration
"""

# ===== GHALA WEBHOOK VERIFICATION =====
def verify_webhook(request):
    """
    Ghala webhook verification function
    Copy this into Ghala's webhook verification section
    """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    # Replace with your verify token
    VERIFY_TOKEN = 'tanzania_service_bot_verify_token'

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return 'Verification failed', 403

# ===== GHALA MESSAGE HANDLER =====
def handle_message(request):
    """
    Handle incoming Ghala WhatsApp messages
    Copy this into Ghala's message handler section
    """
    try:
        data = request.get_json()

        if data and 'messages' in data:
            for message in data['messages']:
                sender_id = message.get('from')
                message_type = message.get('type')

                if message_type == 'text':
                    text = message.get('text', {}).get('body', '')
                    response = process_text_message(text)
                    send_ghala_message(sender_id, response)

                elif message_type == 'location':
                    location_data = message.get('location', {})
                    response = process_location_message(location_data)
                    send_ghala_message(sender_id, response)

        return {'status': 'success'}, 200

    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

# ===== MESSAGE PROCESSING =====
def process_text_message(text):
    """Process text messages and return responses"""
    text_lower = text.lower().strip()

    if 'hi' in text_lower or 'hello' in text_lower:
        return """🇹🇿 *Tanzania Service Finder*

Habari! I'm your AI assistant for finding services in Tanzania.

I can help you find:
🏪 *Auto repair* (karakana)
🏥 *Medical clinics* (kliniki)
✂️ *Hair salons* (kinyozi)
🍽️ *Restaurants* (migahawa)

Send your location or tell me what you need! 📍"""

    elif 'restaurant' in text_lower or 'food' in text_lower:
        return """🍽️ *Popular Restaurants in Dar es Salaam*

🏪 *Beach Banda* - Masaki
   💰 TZS 15,000-45,000
   ⭐ 4.2/5 stars

🏪 *The Terrace* - Masaki
   💰 TZS 25,000-60,000
   ⭐ 4.5/5 stars

🏪 *Addis Ababa Restaurant* - City Center
   💰 TZS 10,000-30,000
   ⭐ 4.0/5 stars

Reply with a name for directions! 🗺️"""

    elif 'directions' in text_lower:
        return """🗺️ *Directions in Dar es Salaam*

I can send you location pins and Google Maps links!

Example requests:
• "directions to Beach Banda"
• "find medical clinics near me"
• "hair salons in Kinondoni"

Share your location first! 📍"""

    else:
        return f"""🤔 I didn't understand: "{text}"

🇹🇿 *Try these:*
• "restaurants" - Find places to eat
• "medical clinics" - Find healthcare
• "hair salons" - Find beauty services
• "directions" - Get navigation help

Or share your location and ask what you need! 📍"""

def process_location_message(location_data):
    """Process location sharing"""
    latitude = location_data.get('latitude')
    longitude = location_data.get('longitude')

    if latitude and longitude:
        return f"""📍 *Location Received!*

📌 Coordinates: {latitude}, {longitude}
🏙️ *Area: Dar es Salaam*

What service are you looking for near this location?

• 🍽️ Restaurants
• 🏥 Medical clinics
• ✂️ Hair salons
• 🚗 Auto repair

Just reply with what you need! 🤖"""

    return "📍 Sorry, I couldn't read the location data. Please try sharing your location again! 🗺️"

# ===== SEND MESSAGE FUNCTION =====
def send_ghala_message(recipient_id, message):
    """
    Send message via Ghala WhatsApp API

    REQUIRED: Configure these in Ghala dashboard
    - GHALA_APP_ID: Your Ghala App ID
    - GHALA_APP_SECRET: Your Ghala App Secret
    """
    import requests

    # REPLACE THESE WITH YOUR ACTUAL CREDENTIALS
    GHALA_APP_ID = "your_ghala_app_id_here"
    GHALA_APP_SECRET = "your_ghala_app_secret_here"

    url = "https://dev.ghala.io/api/v1/messages"

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

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        return response.status_code == 200
    except:
        return False

# ===== LOCATION SENDING =====
def send_location(recipient_id, latitude, longitude, name=None, address=None):
    """
    Send location message via Ghala API
    """
    import requests

    # REPLACE THESE WITH YOUR ACTUAL CREDENTIALS
    GHALA_APP_ID = "your_ghala_app_id_here"
    GHALA_APP_SECRET = "your_ghala_app_secret_here"

    url = "https://dev.ghala.io/api/v1/messages"

    payload = {
        "to": recipient_id,
        "type": "location",
        "location": {
            "latitude": str(latitude),
            "longitude": str(longitude)
        }
    }

    if name:
        payload["location"]["name"] = name
    if address:
        payload["location"]["address"] = address

    headers = {
        "Authorization": f"Bearer {GHALA_APP_SECRET}",
        "Content-Type": "application/json",
        "X-App-Id": GHALA_APP_ID
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        # Also send Google Maps link
        if response.status_code == 200:
            maps_link = f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}"
            text_message = f"""🗺️ *Location sent above!* 📍

🗺️ *Google Maps Link:*
{maps_link}

Tap the pin or click the link for directions! 🚗"""
            send_ghala_message(recipient_id, text_message)

        return response.status_code == 200
    except:
        return False

# ===== USAGE INSTRUCTIONS =====
"""
To use this template in Ghala platform:

1. Copy the verify_webhook() function to your webhook verification endpoint
2. Copy the handle_message() function to your message handler
3. Replace the credentials with your actual Ghala App ID and Secret
4. Configure webhook URL and verify token in Ghala dashboard

Ghala Webhook Configuration:
- Webhook URL: https://your-domain.com/webhook
- Verify Token: tanzania_service_bot_verify_token
- Events: messages, message_deliveries

That's it! Your Tanzania WhatsApp service bot is ready! 🇹🇿🤖📱
"""
