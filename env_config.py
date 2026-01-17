#!/usr/bin/env python3
"""
Environment Configuration for Tanzania Service Chatbot
Configure your Ghala WhatsApp credentials here
"""

import os
from typing import Optional, Dict, Any

class Config:
    """Configuration class for environment variables"""

    # ===== META WHATSAPP BUSINESS API CONFIGURATION =====
    # Get these from Meta WhatsApp Business API (developers.facebook.com)
    WHATSAPP_ACCESS_TOKEN: Optional[str] = os.getenv('WHATSAPP_ACCESS_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    WHATSAPP_WABA_ID: Optional[str] = os.getenv('WHATSAPP_WABA_ID')
    WHATSAPP_WEBHOOK_TOKEN: Optional[str] = os.getenv('WHATSAPP_WEBHOOK_TOKEN', 'tanzania_service_bot_2024')

    # ===== GHALA WHATSAPP API CONFIGURATION =====
    # Get these from Ghala Dashboard (https://dev.ghala.io/)
    GHALA_APP_ID: Optional[str] = os.getenv('GHALA_APP_ID')
    GHALA_APP_SECRET: Optional[str] = os.getenv('GHALA_APP_SECRET')
    GHALA_WEBHOOK_TOKEN: Optional[str] = os.getenv('GHALA_WEBHOOK_TOKEN', 'tanzania_service_bot_ghala')

    # ===== SERVER CONFIGURATION =====
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '5000'))
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'

    # ===== SERVICE CONFIGURATION =====
    # Choose which WhatsApp service to use: 'meta' or 'ghala'
    WHATSAPP_PROVIDER: str = os.getenv('WHATSAPP_PROVIDER', 'ghala')  # Default to Ghala for Tanzania

    # ===== OPENSTREETMAP CONFIGURATION =====
    # Optional: OpenStreetMap API key for enhanced geocoding
    OSM_API_KEY: Optional[str] = os.getenv('OSM_API_KEY')

    @classmethod
    def is_whatsapp_configured(cls) -> bool:
        """Check if WhatsApp credentials are configured"""
        if cls.WHATSAPP_PROVIDER == 'meta':
            return bool(cls.WHATSAPP_ACCESS_TOKEN and cls.WHATSAPP_PHONE_NUMBER_ID)
        elif cls.WHATSAPP_PROVIDER == 'ghala':
            return bool(cls.GHALA_APP_ID and cls.GHALA_APP_SECRET)
        return False

    @classmethod
    def get_whatsapp_credentials(cls) -> Dict[str, Any]:
        """Get the configured WhatsApp credentials"""
        if cls.WHATSAPP_PROVIDER == 'meta':
            return {
                'provider': 'meta',
                'access_token': cls.WHATSAPP_ACCESS_TOKEN,
                'phone_number_id': cls.WHATSAPP_PHONE_NUMBER_ID,
                'waba_id': cls.WHATSAPP_WABA_ID,
                'webhook_token': cls.WHATSAPP_WEBHOOK_TOKEN
            }
        elif cls.WHATSAPP_PROVIDER == 'ghala':
            return {
                'provider': 'ghala',
                'app_id': cls.GHALA_APP_ID,
                'app_secret': cls.GHALA_APP_SECRET,
                'webhook_token': cls.GHALA_WEBHOOK_TOKEN
            }
        return {}

    @classmethod
    def print_setup_instructions(cls):
        """Print setup instructions for missing configuration"""
        print("🇹🇿 Tanzania Service Chatbot - WhatsApp Setup")
        print("=" * 60)
        print()
        print("Choose your WhatsApp provider:")
        print("• 'meta' - Meta WhatsApp Business API (Global)")
        print("• 'ghala' - Ghala WhatsApp API (Tanzania-focused)")
        print()

        if cls.WHATSAPP_PROVIDER == 'meta':
            cls._print_meta_setup()
        elif cls.WHATSAPP_PROVIDER == 'ghala':
            cls._print_ghala_setup()
        else:
            print("⚠️  Invalid WHATSAPP_PROVIDER. Choose 'meta' or 'ghala'")
            cls._print_both_options()

    @classmethod
    def _print_meta_setup(cls):
        """Print Meta WhatsApp setup instructions"""
        print("🌐 META WHATSAPP BUSINESS API SETUP")
        print("-" * 40)
        print()
        print("1. 📝 Set up Meta WhatsApp Business API:")
        print("   - Go to developers.facebook.com")
        print("   - Create a WhatsApp Business API app")
        print("   - Get your Access Token, Phone Number ID, and WABA ID")
        print()
        print("2. ⚙️  Set these environment variables:")
        print("   export WHATSAPP_PROVIDER='meta'")
        print("   export WHATSAPP_ACCESS_TOKEN='your_access_token'")
        print("   export WHATSAPP_PHONE_NUMBER_ID='your_phone_number_id'")
        print("   export WHATSAPP_WABA_ID='your_waba_id'")
        print("   export WHATSAPP_WEBHOOK_TOKEN='your_webhook_token'")
        print()
        print("3. 🌐 Configure webhook in Meta dashboard:")
        print("   - Webhook URL: https://your-domain.com/webhook")
        print("   - Verify token: your_webhook_token")

    @classmethod
    def _print_ghala_setup(cls):
        """Print Ghala WhatsApp setup instructions"""
        print("🇹🇿 GHALA WHATSAPP API SETUP")
        print("-" * 40)
        print()
        print("1. 📝 Sign up for Ghala:")
        print("   - Visit https://dev.ghala.io/")
        print("   - Create a free account")
        print("   - Get your App ID and App Secret")
        print()
        print("2. ⚙️  Set these environment variables:")
        print("   export WHATSAPP_PROVIDER='ghala'")
        print("   export GHALA_APP_ID='your_ghala_app_id'")
        print("   export GHALA_APP_SECRET='your_ghala_app_secret'")
        print("   export GHALA_WEBHOOK_TOKEN='your_webhook_token'")
        print()
        print("3. 🌐 Configure webhook in Ghala dashboard:")
        print("   - Webhook URL: https://your-domain.com/webhook")
        print("   - Verify token: your_webhook_token")

    @classmethod
    def _print_both_options(cls):
        """Print both setup options"""
        print("📋 BOTH PROVIDER OPTIONS:")
        print()
        cls._print_meta_setup()
        print()
        cls._print_ghala_setup()

    @classmethod
    def create_env_file_example(cls):
        """Create an example environment file"""
        env_content = f"""# Tanzania Service Chatbot Environment Configuration
# Choose your WhatsApp provider: 'meta' or 'ghala'
WHATSAPP_PROVIDER=ghala

# ===== META WHATSAPP BUSINESS API =====
# (Use these if WHATSAPP_PROVIDER='meta')
# Get from: https://developers.facebook.com/
WHATSAPP_ACCESS_TOKEN=your_meta_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_meta_phone_number_id_here
WHATSAPP_WABA_ID=your_meta_waba_id_here
WHATSAPP_WEBHOOK_TOKEN=tanzania_service_bot_2024

# ===== GHALA WHATSAPP API =====
# (Use these if WHATSAPP_PROVIDER='ghala')
# Get from: https://dev.ghala.io/
GHALA_APP_ID=your_ghala_app_id_here
GHALA_APP_SECRET=your_ghala_app_secret_here
GHALA_WEBHOOK_TOKEN=tanzania_service_bot_ghala

# ===== SERVER CONFIGURATION =====
HOST=0.0.0.0
PORT=5000
DEBUG=false

# ===== OPTIONAL =====
# OpenStreetMap API key for enhanced geocoding
OSM_API_KEY=your_osm_api_key_here
"""
        return env_content
