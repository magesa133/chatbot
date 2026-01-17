#!/usr/bin/env python3
"""
Test script for WhatsApp location message functionality
Demonstrates how location messages work with Meta WhatsApp Business API
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_models import Location, ServiceProvider
from osm_integration import OpenStreetMapIntegration

def demo_location_message_format():
    """Demonstrate the Meta WhatsApp Business API location message format"""
    print("📍 Meta WhatsApp Business API - Location Message Format")
    print("=" * 60)
    print()

    # Example service provider
    test_provider = ServiceProvider(
        id="test_001",
        name="Test Restaurant Masaki",
        service_type="restaurant",
        location=Location(-6.7572, 39.2763, "Masaki", "Masaki, Dar es Salaam"),
        price_range=(15000, 45000),
        rating=4.2,
        description="Test restaurant in Masaki area",
        accessibility="walking",
        contact_info="+255-XXX-XXXXXX",
        operating_hours="Mon-Sun 7AM-10PM"
    )

    print("🏪 Sample Service Provider:")
    print(f"   Name: {test_provider.name}")
    print(f"   Location: {test_provider.location.latitude}, {test_provider.location.longitude}")
    print(f"   Address: {test_provider.location.name}")
    print(f"   Landmark: {test_provider.location.landmark}")
    print()

    print("📱 Meta WhatsApp API Location Message Format:")
    print("POST https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages")
    print()
    print("Headers:")
    print("  Authorization: Bearer {ACCESS_TOKEN}")
    print("  Content-Type: application/json")
    print()
    print("Body:")
    location_payload = {
        "messaging_product": "whatsapp",
        "to": "255XXXXXXXXX",  # Recipient phone number in E.164 format
        "type": "location",
        "location": {
            "latitude": str(test_provider.location.latitude),
            "longitude": str(test_provider.location.longitude),
            "name": test_provider.name,
            "address": test_provider.location.landmark
        }
    }
    print("  " + str(location_payload).replace("'", '"'))
    print()

    print("🗺️ Google Maps Clickable Link Format:")
    maps_link = f"https://www.google.com/maps/dir/?api=1&destination={test_provider.location.latitude},{test_provider.location.longitude}"
    print(f"   {maps_link}")
    print()

    print("📋 Complete User Experience:")
    print("1. User receives WhatsApp location pin 📍")
    print("2. User receives text message with details and clickable link 🗺️")
    print("3. User can tap location pin to open in WhatsApp Maps")
    print("4. User can click Google Maps link for directions")
    print()

def test_real_location_data():
    """Test with real OpenStreetMap data"""
    print("🌐 Testing with Real OpenStreetMap Data")
    print("=" * 60)

    try:
        # Initialize OSM integration
        osm = OpenStreetMapIntegration()

        # Test location: Masaki, Dar es Salaam
        masaki_location = Location(-6.7572, 39.2763, "Masaki", "Masaki, Dar es Salaam")

        print(f"📍 Searching for restaurants near {masaki_location.name}...")

        # Get real restaurant data
        restaurants = osm.get_service_providers_from_osm("restaurant", masaki_location, max_distance_km=2.0)

        if restaurants:
            print(f"✅ Found {len(restaurants)} restaurants!")
            print()

            # Show first restaurant as example
            restaurant = restaurants[0]
            print("🏪 Example Restaurant Location Message:")
            print(f"   Name: {restaurant.name}")
            print(f"   Coordinates: {restaurant.location.latitude:.4f}, {restaurant.location.longitude:.4f}")
            print(f"   Address: {restaurant.location.landmark or restaurant.location.name}")
            print()

            print("📱 WhatsApp API Payload would be:")
            payload = {
                "messaging_product": "whatsapp",
                "to": "255XXXXXXXXX",
                "type": "location",
                "location": {
                    "latitude": str(restaurant.location.latitude),
                    "longitude": str(restaurant.location.longitude),
                    "name": restaurant.name,
                    "address": restaurant.location.landmark or restaurant.location.name
                }
            }
            print(f"   {payload}")
            print()

            print("🗺️ Google Maps Link:")
            maps_url = f"https://www.google.com/maps/dir/?api=1&destination={restaurant.location.latitude},{restaurant.location.longitude}"
            print(f"   {maps_url}")

        else:
            print("❌ No restaurants found (OpenStreetMap data may be limited)")

    except Exception as e:
        print(f"❌ Error testing real data: {e}")
        print("💡 This might happen if OpenStreetMap dependencies are not installed")

def main():
    """Main test function"""
    print("🇹🇿 Tanzania Service Chatbot - Location Message Testing")
    print("=" * 60)
    print()

    demo_location_message_format()
    print()
    test_real_location_data()

    print()
    print("=" * 60)
    print("✅ Location message testing completed!")
    print()
    print("📝 Summary:")
    print("• Meta WhatsApp Business API location message format demonstrated")
    print("• Google Maps integration for clickable directions")
    print("• Real OpenStreetMap data integration tested")
    print("• Complete user experience flow shown")
    print()
    print("🚀 Ready to send location messages to WhatsApp users!")

if __name__ == "__main__":
    main()
