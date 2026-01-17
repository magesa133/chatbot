#!/usr/bin/env python3
"""
Meta WhatsApp Business API Integration for Tanzania Service Chatbot
Handles WhatsApp messaging via official Meta WhatsApp Business API
"""

import os
import json
import requests
from flask import Flask, request, jsonify
from typing import Dict, Optional, Any
import logging
from main import LocationBasedChatbot
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetaWhatsAppIntegration:
    """Handles WhatsApp integration via Meta WhatsApp Business API"""

    def __init__(self, access_token: str = None, phone_number_id: str = None,
                 waba_id: str = None, webhook_verify_token: str = None):
        """
        Initialize Meta WhatsApp Business API integration

        Args:
            access_token: Meta WhatsApp API Access Token
            phone_number_id: WhatsApp Phone Number ID
            waba_id: WhatsApp Business Account ID
            webhook_verify_token: Webhook verification token
        """
        self.access_token = access_token or os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.phone_number_id = phone_number_id or os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.waba_id = waba_id or os.getenv('WHATSAPP_WABA_ID')
        self.webhook_verify_token = webhook_verify_token or os.getenv('WHATSAPP_WEBHOOK_TOKEN', 'tanzania_service_bot')

        # Meta WhatsApp API endpoints
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
        self.send_message_url = f"{self.base_url}/messages"

        # Initialize chatbot
        self.chatbot = LocationBasedChatbot()

        # Store user sessions (in production, use Redis or database)
        self.user_sessions = {}

        # Flask app for webhook handling
        self.app = Flask(__name__)
        self._setup_routes()

        logger.info("Meta WhatsApp Business API integration initialized")

    def _setup_routes(self):
        """Set up Flask routes for webhook handling"""
        # Routes are defined at the class level to avoid self reference issues
        pass

    def _process_message(self, message: Dict[str, Any]):
        """Process incoming WhatsApp message"""
        try:
            message_type = message.get('type')
            sender_id = message.get('from')
            message_id = message.get('id')

            logger.info(f"Processing message from {sender_id}: {message_type}")

            if message_type == 'text':
                text_content = message.get('text', {}).get('body', '')
                self._handle_text_message(sender_id, text_content, message_id)

            elif message_type == 'location':
                location_data = message.get('location', {})
                self._handle_location_message(sender_id, location_data, message_id)

            else:
                # Handle other message types (images, documents, etc.)
                self._send_message(
                    sender_id,
                    "Sorry, I can only process text messages and location shares right now. Please send me your location or tell me what service you're looking for in Tanzania! 🗺️"
                )

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self._send_message(
                message.get('from'),
                "Sorry, I encountered an error processing your message. Please try again. 😊"
            )

    def _handle_text_message(self, sender_id: str, text: str, message_id: str):
        """Handle text messages"""
        try:
            # Get or create user session
            if sender_id not in self.user_sessions:
                self.user_sessions[sender_id] = {
                    'state': 'welcome',
                    'last_activity': datetime.now()
                }

            # Check if this is a directions request that needs location sending
            if "directions" in text.lower() and hasattr(self.chatbot, 'current_options') and self.chatbot.current_options:
                # Send the service location via WhatsApp location message
                provider = self.chatbot.current_options[0]
                self.send_service_location(sender_id, provider, self.chatbot.user_location)

            # Process message with chatbot
            response = self.chatbot.process_message(text)

            # Send response back to user
            self._send_message(sender_id, response)

            # Update session
            self.user_sessions[sender_id]['last_activity'] = datetime.now()

        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            self._send_message(
                sender_id,
                "Sorry, I had trouble processing your message. Please try again. 🤔"
            )

    def _handle_location_message(self, sender_id: str, location_data: Dict, message_id: str):
        """Handle location messages"""
        try:
            latitude = location_data.get('latitude')
            longitude = location_data.get('longitude')

            if latitude and longitude:
                # Convert coordinates to location name
                from osm_integration import OpenStreetMapIntegration
                osm = OpenStreetMapIntegration()
                location_name = osm.reverse_geocode(latitude, longitude)

                if location_name:
                    location_text = f"GPS coordinates: {latitude:.4f}, {longitude:.4f} (near {location_name})"
                else:
                    location_text = f"GPS coordinates: {latitude:.4f}, {longitude:.4f}"

                # Process as location input
                response = self.chatbot.process_message(location_text)
                self._send_message(sender_id, f"📍 Location received! {response}")
            else:
                self._send_message(
                    sender_id,
                    "Sorry, I couldn't read the location data. Please try sharing your location again or tell me your location in text format. 🗺️"
                )

        except Exception as e:
            logger.error(f"Error handling location message: {e}")
            self._send_message(
                sender_id,
                "Sorry, I had trouble processing your location. Please try again. 📍"
            )

    def _send_message(self, recipient_id: str, message: str):
        """Send message via Meta WhatsApp Business API"""
        try:
            if not self.access_token or not self.phone_number_id:
                logger.error("Meta WhatsApp credentials not configured")
                return False

            # Format message for WhatsApp
            formatted_message = self._format_message_for_whatsapp(message)

            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_id,
                "type": "text",
                "text": {
                    "body": formatted_message
                }
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                self.send_message_url,
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"Message sent successfully to {recipient_id}")
                return True
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    def _format_message_for_whatsapp(self, message: str) -> str:
        """Format message for WhatsApp (character limits, emojis, etc.)"""
        # WhatsApp has a 4096 character limit per message
        if len(message) > 4000:
            # Split long messages (simplified - in production, handle properly)
            message = message[:4000] + "...\n\n💡 Message was truncated. Reply 'more' for additional details."

        # Ensure message is properly encoded
        return message.strip()

    def send_location(self, recipient_id: str, latitude: float, longitude: float,
                     name: str = None, address: str = None) -> bool:
        """
        Send a location message to a WhatsApp user

        Args:
            recipient_id: WhatsApp recipient ID
            latitude: Location latitude
            longitude: Location longitude
            name: Location name (optional)
            address: Location address (optional)
        """
        try:
            if not self.access_token or not self.phone_number_id:
                logger.error("Meta WhatsApp credentials not configured")
                return False

            payload = {
                "messaging_product": "whatsapp",
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
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                self.send_message_url,
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                logger.info(f"Location sent successfully to {recipient_id}")
                return True
            else:
                logger.error(f"Failed to send location: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error sending location: {e}")
            return False

    def send_service_location(self, recipient_id: str, service_provider, user_location=None):
        """
        Send a service provider location with clickable map link

        Args:
            recipient_id: WhatsApp recipient ID
            service_provider: ServiceProvider object with location info
            user_location: Optional user location for distance calculation
        """
        try:
            # First send location via WhatsApp location message
            location_sent = self.send_location(
                recipient_id=recipient_id,
                latitude=service_provider.location.latitude,
                longitude=service_provider.location.longitude,
                name=service_provider.name,
                address=service_provider.location.landmark or service_provider.location.name
            )

            # Then send text message with clickable Google Maps link
            if location_sent:
                maps_link = f"https://www.google.com/maps/dir/?api=1&destination={service_provider.location.latitude},{service_provider.location.longitude}"

                distance_text = ""
                if user_location:
                    distance = user_location.distance_to(service_provider.location)
                    distance_text = f" ({distance:.1f}km away)"

                message = f"""
📍 *{service_provider.name}*
🏷️ {service_provider.location.name}{distance_text}

🗺️ *View on Google Maps:*
{maps_link}

📞 Contact: {service_provider.contact_info}
🕒 Hours: {service_provider.operating_hours}
💰 Price: TZS {service_provider.price_range[0]}-{service_provider.price_range[1]}

🚶 *Accessibility:* {service_provider.accessibility.replace('_', ' ').title()}
"""

                return self._send_message(recipient_id, message)

            return False

        except Exception as e:
            logger.error(f"Error sending service location: {e}")
            return False

    def send_welcome_message(self, recipient_id: str):
        """Send welcome message to new users"""
        welcome_text = """🇹🇿 *Tanzania Service Finder*

Karibu! I'm your AI assistant for finding services in Tanzania.

I can help you find:
🏪 *Auto repair* (karakana)
🏥 *Medical services* (kliniki)
✂️ *Hair salons* (kinyozi)
🍽️ *Restaurants* (migahawa)
🔧 *Plumbing & Electrical*
🏠 *Cleaning services*

*How to use:*
1. Share your location 📍
2. Tell me what service you need
3. Get instant recommendations!

Example: "I need a restaurant in Masaki"

Send your location or ask me anything! 🤖"""

        return self._send_message(recipient_id, welcome_text)

    def run_webhook_server(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the Flask webhook server"""
        logger.info(f"Starting webhook server on {host}:{port}")
        print(f"🚀 WhatsApp Chatbot Server Starting...")
        print(f"📱 Webhook URL: http://{host}:{port}/webhook")
        print(f"❤️  Health Check: http://{host}:{port}/health")
        print(f"🇹🇿 Ready to serve Tanzania!")
        print("=" * 50)

        self.app.run(host=host, port=port, debug=debug)

    def test_connection(self) -> bool:
        """Test connection to Meta WhatsApp Business API"""
        try:
            # Test by sending a simple message or checking phone number status
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            # Try to get phone number info
            test_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"
            response = requests.get(test_url, headers=headers, timeout=10)

            if response.status_code in [200, 400]:  # 400 might mean invalid request but API is reachable
                logger.info("Meta WhatsApp API connection test successful")
                return True
            else:
                logger.error(f"Meta WhatsApp API test failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Meta WhatsApp API connection test error: {e}")
            return False


def create_app():
    """Factory function to create Flask app with WhatsApp integration"""
    # Load environment variables
    app_id = os.getenv('GHALA_APP_ID')
    app_secret = os.getenv('GHALA_APP_SECRET')
    webhook_token = os.getenv('GHALA_WEBHOOK_TOKEN', 'tanzania_service_bot')

    # Create integration instance
    whatsapp = GhalaWhatsAppIntegration(
        app_id=app_id,
        app_secret=app_secret,
        webhook_verify_token=webhook_token
    )

    return whatsapp.app, whatsapp


# Standalone script to run the server
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Tanzania WhatsApp Service Chatbot')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--test', action='store_true', help='Test Ghala API connection')

    args = parser.parse_args()

    # Create WhatsApp integration
    whatsapp = GhalaWhatsAppIntegration()

    if args.test:
        print("🧪 Testing Ghala API connection...")
        if whatsapp.test_connection():
            print("✅ Ghala API connection successful!")
        else:
            print("❌ Ghala API connection failed. Check your credentials.")
        exit(0)

    # Check if credentials are configured
    if not whatsapp.app_id or not whatsapp.app_secret:
        print("⚠️  Warning: Ghala credentials not found!")
        print("Please set these environment variables:")
        print("  export GHALA_APP_ID='your_app_id'")
        print("  export GHALA_APP_SECRET='your_app_secret'")
        print("  export GHALA_WEBHOOK_TOKEN='your_webhook_token'")
        print()

    # Run the server
    whatsapp.run_webhook_server(host=args.host, port=args.port, debug=args.debug)
