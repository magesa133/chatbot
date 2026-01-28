#!/usr/bin/env python3
"""
Test script for the SQLite database functionality
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from webhook_server import DatabaseManager

def test_database():
    """Test basic database operations"""
    print("🧪 Testing Tanzania Services Database")
    print("=" * 50)

    # Initialize database
    db = DatabaseManager()

    # Test user registration
    print("\n👤 Testing User Registration:")
    user = db.register_user("+255712345678", "Test User")
    if user:
        print(f"✅ User registered: {user['name']} (ID: {user['id']})")
        user_id = user['id']
    else:
        print("❌ User registration failed")
        return

    # Test location update
    print("\n📍 Testing Location Update:")
    success = db.update_user_location("+255712345678", -6.8167, 39.2892, "Test Location")
    print(f"✅ Location updated: {success}")

    # Test service provider retrieval
    print("\n🏪 Testing Service Providers:")
    restaurants = db.get_service_providers('restaurant', limit=2)
    print(f"Found {len(restaurants)} restaurants")

    for restaurant in restaurants:
        print(f"  • {restaurant['name']} - {restaurant['location_name']} (Rating: {restaurant['rating']}/5)")

    # Test booking creation
    print("\n📅 Testing Booking Creation:")
    booking = db.create_booking(
        user_id=user_id,
        provider_id=1,  # Beach Banda
        service_type='restaurant',
        booking_date='2024-01-20',
        booking_time='19:00',
        notes='Test booking from database test'
    )

    if booking:
        print(f"✅ Booking created: #{booking['id']} - {booking['service_type']} at {booking['booking_date']} {booking['booking_time']}")
    else:
        print("❌ Booking creation failed")

    # Test review system
    print("\n⭐ Testing Review System:")
    review_success = db.add_review(user_id, 1, 5, "Excellent service and food!")
    print(f"✅ Review added: {review_success}")

    # Get reviews
    reviews = db.get_provider_reviews(1, limit=2)
    print(f"Provider now has {len(reviews)} reviews")

    # Test user bookings
    print("\n📋 Testing User Bookings:")
    bookings = db.get_user_bookings(user_id)
    print(f"User has {len(bookings)} bookings")

    for booking in bookings:
        print(f"  • Booking #{booking['id']}: {booking['service_type']} at {booking['provider_name']}")

    # Test location-based search
    print("\n🗺️ Testing Location-Based Search:")
    nearby_restaurants = db.search_providers_near_location(-6.8167, 39.2892, 'restaurant', 10.0)
    print(f"Found {len(nearby_restaurants)} restaurants within 10km")

    for restaurant in nearby_restaurants[:2]:
        print(f"  • {restaurant['name']} - {restaurant['distance_km']} km away")

    print("\n🎉 Database tests completed successfully!")
    print("\n📊 Database file: tanzania_services.db")
    print("💡 You can now explore the database with: sqlite3 tanzania_services.db")

if __name__ == "__main__":
    test_database()
