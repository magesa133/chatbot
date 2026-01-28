#!/usr/bin/env python3
"""
Demo script showing how the enhanced Tanzania Services chatbot responds
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from webhook_server import process_message

def demo_responses():
    """Demonstrate how the system responds to different commands"""

    print("🇹🇿 Tanzania Services Chatbot - Enhanced Responses Demo")
    print("=" * 60)

    test_cases = [
        ("hi", "Greeting/Welcome"),
        ("restaurants", "General restaurant listing"),
        ("restaurants near me", "Location-based restaurant search"),
        ("book restaurant at Beach Banda tomorrow 7pm", "Booking request"),
        ("review Beach Banda 5 Excellent seafood!", "Review submission"),
        ("my bookings", "View user bookings"),
        ("see reviews Beach Banda", "View reviews"),
        ("medical clinics", "Medical services"),
        ("hair salons near me", "Beauty services with location"),
        ("emergency", "Emergency services"),
    ]

    sender_id = "+255614062161"  # Test user from our database

    for message, description in test_cases:
        print(f"\n🔸 {description}")
        print(f"User: '{message}'")
        print("-" * 40)

        response = process_message(message, sender_id)

        # Truncate long responses for display
        if len(response) > 500:
            response = response[:500] + "...\n\n[Response truncated for demo]"

        print(f"Bot: {response}")
        print("-" * 40)

    print("\n🎉 Demo completed!")
    print("\n💡 Key Features Now Available:")
    print("• 📍 Location-aware service discovery")
    print("• 📅 Real appointment booking system")
    print("• ⭐ Review and rating system")
    print("• 👤 User registration and profiles")
    print("• 📊 Message history and analytics")
    print("• 🗄️ Persistent SQLite database")
    print("• 🔍 Advanced search and filtering")

if __name__ == "__main__":
    demo_responses()
