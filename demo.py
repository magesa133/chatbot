#!/usr/bin/env python3
"""
Demo script showcasing the Location-Based Service Search Chatbot
A complete conversation example.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import LocationBasedChatbot


def demo_conversation():
    """Demonstrate a complete conversation with the chatbot"""
    print("🎬 LOCATION-BASED SERVICE SEARCH CHATBOT DEMO")
    print("=" * 60)
    print("This demo shows a complete conversation flow.")
    print("In a real scenario, this would be a WhatsApp conversation.")
    print()

    chatbot = LocationBasedChatbot()

    # Complete conversation flow
    conversation = [
        ("", "👋 Welcome message"),
        ("Manhattan near Times Square", "📍 Location input with landmark"),
        ("auto repair", "🔧 Service selection"),
        ("mid-range", "💰 Budget preference"),
        ("compare", "📊 Request comparison"),
        ("1", "☝️ Select first option for details"),
        ("directions", "🗺️ Request directions"),
        ("new", "🔄 Start new search"),
        ("Brooklyn", "📍 New location"),
        ("hair salon", "✂️ New service"),
        ("under $50", "💸 Budget constraint"),
        ("1", "☝️ Select option"),
        ("call", "📞 Request to call"),
        ("quit", "👋 End conversation")
    ]

    print("💬 CONVERSATION FLOW:")
    print("-" * 40)

    for user_input, description in conversation:
        if user_input == "quit":
            print(f"\n👤 {description}: {user_input}")
            print("🤖 Bot: 👋 Goodbye! Thanks for using our service finder.")
            break

        print(f"\n👤 {description}: '{user_input}'")

        if user_input:  # Skip empty welcome message
            response = chatbot.process_message(user_input)
        else:
            response = chatbot.process_message("")

        print("🤖 Bot:")  # Clean up the response for display
        response_lines = response.split('\n')
        for line in response_lines:
            if line.strip():
                print(f"   {line}")

        print("-" * 40)

    print("\n" + "=" * 60)
    print("✅ DEMO COMPLETED!")
    print("\nKey Features Demonstrated:")
    print("• ✅ Location-based search (GPS, town, landmark)")
    print("• ✅ Service type recognition")
    print("• ✅ Budget-aware filtering")
    print("• ✅ Proximity-based sorting")
    print("• ✅ Option comparison")
    print("• ✅ Detailed provider information")
    print("• ✅ Accessibility indicators")
    print("• ✅ Directions and contact info")
    print("• ✅ Conversational flow with state management")
    print("• ✅ WhatsApp-friendly messaging")
    print("\n🚀 Ready for production use!")
    print("Integrate with WhatsApp Business API, Telegram, or web interface.")


if __name__ == "__main__":
    demo_conversation()
