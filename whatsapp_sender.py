#!/usr/bin/env python3
"""
WhatsApp Message Sender for Tanzania Service Chatbot
Send WhatsApp messages using actual credentials from .env file
Supports both Meta and Ghala WhatsApp providers
"""

import requests
import logging
from dotenv import load_dotenv
from env_config import Config

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def send_whatsapp_message(to_number: str, message: str):
    """
    Send a WhatsApp message using the configured provider

    Args:
        to_number: Recipient phone number (E.164 format, e.g., "255612062161")
        message: Message content

    Returns:
        bool: True if message sent successfully, False otherwise
    """

    if not Config.is_whatsapp_configured():
        print("❌ WhatsApp not configured. Please check your .env file and environment variables.")
        return False

    print(f"📱 Provider: {Config.WHATSAPP_PROVIDER.upper()}")
    print(f"📤 Sending message to {to_number}...")
    print(f"📝 Message: {message[:50]}{'...' if len(message) > 50 else ''}")
    print()

    try:
        if Config.WHATSAPP_PROVIDER == 'meta':
            return send_meta_message(to_number, message)
        elif Config.WHATSAPP_PROVIDER == 'ghala':
            return send_ghala_message(to_number, message)
        else:
            print(f"❌ Unsupported provider: {Config.WHATSAPP_PROVIDER}")
            return False

    except Exception as e:
        print(f"❌ Error sending message: {e}")
        logger.error(f"Message send error: {e}")
        return False

def send_meta_message(to_number: str, message: str):
    """Send message via Meta WhatsApp Business API"""
    url = f"https://graph.facebook.com/v18.0/{Config.WHATSAPP_PHONE_NUMBER_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }

    headers = {
        "Authorization": f"Bearer {Config.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)

    if response.status_code == 200:
        result = response.json()
        message_id = result.get('messages', [{}])[0].get('id')
        print("✅ Message sent successfully via Meta API!")
        print(f"📨 Message ID: {message_id}")
        return True
    else:
        print(f"❌ Failed to send message via Meta API: {response.status_code}")
        print(f"📄 Response: {response.text}")
        return False

def send_ghala_message(to_number: str, message: str):
    """Send message via Ghala WhatsApp API"""
    url = "https://dev.ghala.io/api/v1/messages"

    payload = {
        "to": to_number,
        "type": "text",
        "text": {"body": message}
    }

    headers = {
        "Authorization": f"Bearer {Config.GHALA_APP_SECRET}",
        "Content-Type": "application/json",
        "X-App-Id": Config.GHALA_APP_ID
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)

    if response.status_code == 200:
        result = response.json()
        message_id = result.get('message_id')
        print("✅ Message sent successfully via Ghala API!")
        print(f"📨 Message ID: {message_id}")
        return True
    else:
        print(f"❌ Failed to send message via Ghala API: {response.status_code}")
        print(f"📄 Response: {response.text}")
        return False

def main():
    """Main function to send WhatsApp messages"""
    print("🇹🇿 Tanzania Service Chatbot - WhatsApp Message Sender")
    print("=" * 60)

    # Check configuration
    if not Config.is_whatsapp_configured():
        print("❌ WhatsApp credentials not configured!")
        print("\nPlease check your .env file and ensure you have set:")
        if Config.WHATSAPP_PROVIDER == 'meta':
            print("  WHATSAPP_ACCESS_TOKEN")
            print("  WHATSAPP_PHONE_NUMBER_ID")
        elif Config.WHATSAPP_PROVIDER == 'ghala':
            print("  GHALA_APP_ID")
            print("  GHALA_APP_SECRET")
        else:
            print("  Valid WHATSAPP_PROVIDER ('meta' or 'ghala')")
        return

    print(f"✅ WhatsApp configured for {Config.WHATSAPP_PROVIDER.upper()} API")
    print()

    # Get message details from user
    try:
        recipient = input("📱 Enter recipient phone number (E.164 format, e.g., 255612062161): ").strip()
        if not recipient:
            print("❌ No recipient specified.")
            return

        # Validate phone number format
        if not recipient.startswith('+') and not recipient.startswith('255'):
            print("⚠️  Phone number should be in E.164 format (start with country code)")
            if input("Continue anyway? (y/N): ").lower().strip() != 'y':
                return

        message = input("💬 Enter message to send: ").strip()
        if not message:
            print("❌ No message specified.")
            return

        print(f"\n📋 Message Details:")
        print(f"📱 To: {recipient}")
        print(f"💬 Message: {message}")
        print(f"📏 Length: {len(message)} characters")

        # Confirmation
        confirm = input(f"\n⚠️  Send this message? (yes/no): ").lower().strip()
        if confirm not in ['yes', 'y', 'true']:
            print("❌ Message cancelled.")
            return

        print("\n📤 Sending message...")
        success = send_whatsapp_message(recipient, message)

        if success:
            print("\n🎉 MESSAGE SENT SUCCESSFULLY!")
            print("📱 Check the recipient's WhatsApp for the message.")
        else:
            print("\n❌ MESSAGE FAILED!")
            print("🔧 Check your WhatsApp API configuration and credentials.")
            print("📋 Verify API permissions and recipient number format.")

    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Main function error: {e}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
