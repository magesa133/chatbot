#!/usr/bin/env python3
"""
Test script for the Location-Based Service Search Chatbot
Demonstrates various conversation flows and functionality.
"""

import sys
import os

# Add current directory to path so we can import main module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import LocationBasedChatbot


def simulate_conversation(chatbot, messages):
    """Simulate a conversation with the chatbot"""
    print(f"\n{'='*60}")
    print("🤖 SIMULATED CONVERSATION")
    print(f"{'='*60}")

    for i, user_msg in enumerate(messages, 1):
        print(f"\n👤 User {i}: {user_msg}")
        response = chatbot.process_message(user_msg)
        print(f"🤖 Bot {i}: {response}")
        print("-" * 40)


def test_basic_flow():
    """Test basic conversation flow"""
    print("\n🧪 TEST 1: Basic Auto Repair Search")
    chatbot = LocationBasedChatbot()

    messages = [
        "",  # Start conversation
        "Manhattan near Times Square",
        "auto repair",
        "under $100",
        "1",  # Select first option
        "directions",
        "new"  # Start new search
    ]

    simulate_conversation(chatbot, messages)


def test_budget_comparison():
    """Test budget-aware recommendations and comparison"""
    print("\n🧪 TEST 2: Budget Comparison for Hair Salon")
    chatbot = LocationBasedChatbot()

    messages = [
        "",
        "Brooklyn near Prospect Park",
        "hair salon",
        "mid-range",
        "compare",
        "2",
        "call",
        "back"
    ]

    simulate_conversation(chatbot, messages)


def test_medical_services():
    """Test medical service search"""
    print("\n🧪 TEST 3: Medical Services Search")
    chatbot = LocationBasedChatbot()

    messages = [
        "",
        "Queens near Forest Hills",
        "medical clinic",
        "no preference",
        "more",
        "1",
        "compare"
    ]

    simulate_conversation(chatbot, messages)


def test_no_results_scenario():
    """Test scenario with no matching results"""
    print("\n🧪 TEST 4: No Results Scenario")
    chatbot = LocationBasedChatbot()

    messages = [
        "",
        "Remote location",
        "specialized service that doesn't exist",
        "premium budget"
    ]

    simulate_conversation(chatbot, messages)


def test_location_parsing():
    """Test different location input formats"""
    print("\n🧪 TEST 5: Location Parsing Variations")
    test_cases = [
        ("Manhattan", "Basic city name"),
        ("Central Park", "Landmark reference"),
        ("40.7128,-74.0060", "GPS coordinates (would need enhancement)"),
        ("Unknown location", "Unrecognized location")
    ]

    for location, description in test_cases:
        print(f"\n📍 Testing: {description} - '{location}'")
        chatbot = LocationBasedChatbot()
        response = chatbot.process_message("")  # Welcome
        response = chatbot.process_message(location)  # Location input
        print(f"🤖 Bot: {response}")


def run_all_tests():
    """Run all test scenarios"""
    print("🧪 LOCATION-BASED CHATBOT TEST SUITE")
    print("=" * 60)

    test_basic_flow()
    test_budget_comparison()
    test_medical_services()
    test_no_results_scenario()
    test_location_parsing()

    print(f"\n{'='*60}")
    print("✅ All tests completed!")
    print("Review the output above to verify chatbot behavior.")
    print(f"{'='*60}")


def interactive_test():
    """Run interactive test mode"""
    print("🎮 INTERACTIVE TEST MODE")
    print("Type 'quit' to exit, 'test' to run automated tests")
    print("-" * 50)

    chatbot = LocationBasedChatbot()

    while True:
        user_input = input("\n👤 You: ").strip()

        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\n👋 Goodbye! Thanks for testing.")
            break
        elif user_input.lower() == 'test':
            run_all_tests()
            continue

        response = chatbot.process_message(user_input)
        print(f"🤖 Bot: {response}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_test()
    else:
        run_all_tests()
