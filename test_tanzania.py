#!/usr/bin/env python3
"""
Tanzania/Dar es Salaam specific test script for the OpenStreetMap integration.
Tests real location data and service provider discovery.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from osm_integration import OpenStreetMapIntegration, TanzaniaLocations
from data_models import Location


def test_tanzania_locations():
    """Test Tanzania location recognition and geocoding"""
    print("🗺️ TESTING TANZANIA LOCATION RECOGNITION")
    print("=" * 50)

    locations_to_test = [
        "dar es salaam",
        "masaki",
        "kinondoni",
        "posta",
        "kariakoo",
        "arusha",
        "dodoma",
        "mwanza",
        "airport",
        "university"
    ]

    for location_text in locations_to_test:
        print(f"\n📍 Testing: '{location_text}'")
        result = TanzaniaLocations.get_location_from_text(location_text)
        if result:
            print(f"   ✅ Found: {result.name} at ({result.latitude:.4f}, {result.longitude:.4f})")
        else:
            print("   ❌ Not found in Tanzania locations")


def test_openstreetmap_geocoding():
    """Test OpenStreetMap geocoding for Tanzania"""
    print("\n\n🌐 TESTING OPENSTREETMAP GEOCODING")
    print("=" * 50)

    osm = OpenStreetMapIntegration()

    locations_to_test = [
        "Dar es Salaam Posta",
        "Masaki Dar es Salaam",
        "University of Dar es Salaam",
        "Kariakoo Market",
        "Julius Nyerere International Airport"
    ]

    for location_text in locations_to_test:
        print(f"\n📍 Geocoding: '{location_text}'")
        try:
            result = osm.geocode_location(location_text)
            if result:
                print(f"   ✅ Found: {result.name} at ({result.latitude:.4f}, {result.longitude:.4f})")
                print(f"      Landmark: {result.landmark}")
            else:
                print("   ❌ Not found via OpenStreetMap")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_service_provider_discovery():
    """Test real service provider discovery from OpenStreetMap"""
    print("\n\n🏪 TESTING SERVICE PROVIDER DISCOVERY")
    print("=" * 50)

    osm = OpenStreetMapIntegration()

    # Test location: Masaki, Dar es Salaam (popular area)
    test_location = Location(-6.75, 39.27, "Masaki", "Masaki, Dar es Salaam")

    services_to_test = ["restaurant", "medical", "hair_salon"]

    for service in services_to_test:
        print(f"\n🔍 Searching for {service} near {test_location.name}")
        try:
            providers = osm.get_service_providers_from_osm(service, test_location, max_distance_km=5.0)
            print(f"   Found {len(providers)} providers:")

            for i, provider in enumerate(providers[:3], 1):  # Show first 3
                distance = test_location.distance_to(provider.location)
                print(f"      {i}. {provider.name}")
                print(f"         📍 {provider.location.name} ({distance:.1f}km)")
                print(f"         💰 {provider.price_range[0]}-{provider.price_range[1]} TZS")
                print(f"         🚶 {provider.accessibility}")

        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_nearby_landmarks():
    """Test nearby landmarks discovery"""
    print("\n\n🏛️ TESTING NEARBY LANDMARKS")
    print("=" * 50)

    osm = OpenStreetMapIntegration()

    # Test location: Central Dar es Salaam
    test_location = Location(-6.8167, 39.2833, "Central Dar es Salaam", "Posta")

    print(f"🗺️ Finding landmarks near {test_location.name}")
    try:
        landmarks = osm.get_nearby_landmarks(test_location, max_distance_km=3.0)
        print(f"Found {len(landmarks)} nearby landmarks:")
        for landmark in landmarks:
            print(f"   • {landmark}")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_distance_calculations():
    """Test distance calculations between Tanzania locations"""
    print("\n\n📏 TESTING DISTANCE CALCULATIONS")
    print("=" * 50)

    locations = [
        ("Dar es Salaam", Location(-6.7924, 39.2083, "Dar es Salaam", "Central")),
        ("Arusha", Location(-3.3667, 36.6833, "Arusha", "Central")),
        ("Dodoma", Location(-6.1730, 35.7419, "Dodoma", "Central")),
        ("Mwanza", Location(-2.5167, 32.9000, "Mwanza", "Central"))
    ]

    print("Distances from Dar es Salaam:")
    dar_location = locations[0][1]
    for name, location in locations[1:]:
        distance = dar_location.distance_to(location)
        print(".1f")


def run_all_tanzania_tests():
    """Run all Tanzania-specific tests"""
    print("🇹🇿 TANZANIA SERVICE CHATBOT - OPENSTREETMAP INTEGRATION TESTS")
    print("=" * 70)

    try:
        test_tanzania_locations()
        test_openstreetmap_geocoding()
        test_service_provider_discovery()
        test_nearby_landmarks()
        test_distance_calculations()

        print("\n" + "=" * 70)
        print("✅ All Tanzania tests completed!")
        print("Note: Some tests may show limited results if OpenStreetMap data for Tanzania is sparse.")
        print("The system gracefully falls back to static data when OSM queries fail.")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tanzania_tests()
