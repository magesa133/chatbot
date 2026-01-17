#!/usr/bin/env python3
"""
Location-Based Service Search Chatbot
A conversational chatbot for finding nearby service providers with budget considerations.
"""

import json
import sys
from typing import Dict, List, Optional, Tuple
from enum import Enum
from data_models import Location, ServiceProvider, BudgetRange
from config import (
    CHATBOT_CONFIG, RESPONSE_TEMPLATES, ACCESSIBILITY_GUIDES,
    load_service_providers, get_location_from_text, get_service_type_from_text
)
try:
    from osm_integration import OpenStreetMapIntegration
    OSM_AVAILABLE = True
except ImportError:
    print("Warning: OpenStreetMap integration not available. Using fallback mode.")
    OSM_AVAILABLE = False


class ChatState(Enum):
    """Chat conversation states"""
    WELCOME = "welcome"
    ASK_LOCATION = "ask_location"
    ASK_SERVICE = "ask_service"
    ASK_BUDGET = "ask_budget"
    SHOW_RESULTS = "show_results"
    COMPARE_OPTIONS = "compare_options"
    GET_MORE_DETAILS = "get_more_details"
    CONFIRM_CHOICE = "confirm_choice"


class LocationBasedChatbot:
    """Main chatbot class for location-based service search"""

    def __init__(self):
        self.state = ChatState.WELCOME
        self.user_location: Optional[Location] = None
        self.selected_service: Optional[str] = None
        self.budget_range: Optional[Tuple[float, float]] = None
        self.search_results: List[ServiceProvider] = []
        self.current_options: List[ServiceProvider] = []
        self.providers_db = self._load_providers_database()
        self.osm_integration = OpenStreetMapIntegration() if OSM_AVAILABLE else None

    def _load_providers_database(self) -> List[ServiceProvider]:
        """Load service providers from configuration"""
        return load_service_providers()

    def get_budget_category(self, price_range: Tuple[float, float]) -> BudgetRange:
        """Categorize price range into budget categories"""
        avg_price = (price_range[0] + price_range[1]) / 2
        if avg_price <= 50:
            return BudgetRange.LOW_COST
        elif avg_price <= 150:
            return BudgetRange.MID_RANGE
        else:
            return BudgetRange.PREMIUM

    def search_providers(self, service_type: str, user_location: Location,
                        max_distance: Optional[float] = None,
                        budget_range: Optional[Tuple[float, float]] = None) -> List[ServiceProvider]:
        """Search for service providers based on criteria using OpenStreetMap data"""
        if max_distance is None:
            max_distance = CHATBOT_CONFIG["max_search_distance_km"]

        results = []

        # First try to get real providers from OpenStreetMap
        if OSM_AVAILABLE and self.osm_integration:
            try:
                osm_providers = self.osm_integration.get_service_providers_from_osm(
                    service_type, user_location, max_distance
                )
                results.extend(osm_providers)
            except Exception as e:
                print(f"Error fetching OSM data: {e}")
                # Fall back to static database if OSM fails
            for provider in self.providers_db:
                if provider.service_type != service_type:
                    continue

                distance = user_location.distance_to(provider.location)
                if distance > max_distance:
                    continue

                if budget_range:
                    # Check if provider's price range overlaps with user's budget
                    if not (provider.price_range[1] >= budget_range[0] and
                           provider.price_range[0] <= budget_range[1]):
                        continue

                results.append(provider)

        # If no OSM results, fall back to static database
        if not results:
            print("No OSM results found, falling back to static database")
            for provider in self.providers_db:
                if provider.service_type != service_type:
                    continue

                distance = user_location.distance_to(provider.location)
                if distance > max_distance:
                    continue

                if budget_range:
                    # Check if provider's price range overlaps with user's budget
                    if not (provider.price_range[1] >= budget_range[0] and
                           provider.price_range[0] <= budget_range[1]):
                        continue

                results.append(provider)

        # Apply budget filtering to OSM results
        if budget_range:
            filtered_results = []
            for provider in results:
                if (provider.price_range[1] >= budget_range[0] and
                    provider.price_range[0] <= budget_range[1]):
                    filtered_results.append(provider)
            results = filtered_results

        # Sort by distance
        results.sort(key=lambda p: user_location.distance_to(p.location))
        return results

    def format_provider_info(self, provider: ServiceProvider, user_location: Location) -> str:
        """Format provider information for display"""
        distance = user_location.distance_to(provider.location)
        budget_cat = self.get_budget_category(provider.price_range)

        accessibility_notes = {
            "walking": "🚶 Walking distance",
            "public_transport": "🚇 Public transport accessible",
            "vehicle": "🚗 Vehicle required"
        }

        return f"""🏢 {provider.name}
💰 Price: ${provider.price_range[0]}-${provider.price_range[1]} ({budget_cat.value})
📍 Distance: {distance:.1f} km from your location
📍 Location: {provider.location.name} (near {provider.location.landmark})
{accessibility_notes[provider.accessibility]}
⭐ Rating: {provider.rating}/5
🕒 Hours: {provider.operating_hours}
📞 Contact: {provider.contact_info}
📝 {provider.description}

"""

    def process_message(self, user_message: str) -> str:
        """Process user message and return chatbot response"""
        message = user_message.lower().strip()

        if self.state == ChatState.WELCOME:
            return self._handle_welcome()

        elif self.state == ChatState.ASK_LOCATION:
            return self._handle_location_input(message)

        elif self.state == ChatState.ASK_SERVICE:
            return self._handle_service_input(message)

        elif self.state == ChatState.ASK_BUDGET:
            return self._handle_budget_input(message)

        elif self.state == ChatState.SHOW_RESULTS:
            return self._handle_results_interaction(message)

        elif self.state == ChatState.COMPARE_OPTIONS:
            return self._handle_comparison(message)

        elif self.state == ChatState.GET_MORE_DETAILS:
            return self._handle_more_details(message)

        elif self.state == ChatState.CONFIRM_CHOICE:
            return self._handle_confirmation(message)

        return "I'm sorry, I didn't understand that. Let me start over.\n" + self._handle_welcome()

    def _handle_welcome(self) -> str:
        """Handle initial welcome and start conversation"""
        self.state = ChatState.ASK_LOCATION
        return RESPONSE_TEMPLATES["welcome"]

    def _handle_location_input(self, message: str) -> str:
        """Handle user location input"""
        self.user_location = get_location_from_text(message)
        self.state = ChatState.ASK_SERVICE

        return RESPONSE_TEMPLATES["location_confirm"].format(
            location=self.user_location.name,
            service_options=RESPONSE_TEMPLATES["service_options"]
        )

    def _handle_service_input(self, message: str) -> str:
        """Handle service type selection"""
        self.selected_service = get_service_type_from_text(message)
        self.state = ChatState.ASK_BUDGET

        budget_ranges = CHATBOT_CONFIG["default_budget_ranges"]

        return RESPONSE_TEMPLATES["budget_prompt"].format(
            service=self.selected_service.replace('_', ' '),
            low_max=budget_ranges["low_cost"][1],
            mid_min=budget_ranges["mid_range"][0],
            mid_max=budget_ranges["mid_range"][1],
            premium_min=budget_ranges["premium"][0]
        )

    def _handle_budget_input(self, message: str) -> str:
        """Handle budget input and show results"""
        if "no preference" in message or "any" in message or "doesn't matter" in message:
            self.budget_range = None
        elif "low" in message or "under" in message or "cheap" in message:
            self.budget_range = (0, 50)
        elif "mid" in message or "medium" in message:
            self.budget_range = (50, 150)
        elif "premium" in message or "expensive" in message:
            self.budget_range = (150, 1000)
        else:
            # Try to parse specific amounts
            import re
            numbers = re.findall(r'\d+', message)
            if numbers:
                max_budget = int(numbers[0])
                self.budget_range = (0, max_budget)
            else:
                self.budget_range = None

        # Search for providers
        self.search_results = self.search_providers(
            self.selected_service,
            self.user_location,
            budget_range=self.budget_range
        )

        if not self.search_results:
            # No exact matches, try broader search
            self.search_results = self.search_providers(
                self.selected_service,
                self.user_location,
                max_distance=20.0  # Increase search radius
            )

        self.state = ChatState.SHOW_RESULTS

        if not self.search_results:
            return """Sorry, I couldn't find any providers for that service in your area.

Would you like to:
1. Try a different service type
2. Search in a different location
3. Or let me know what you're looking for specifically?"""

        # Show top 3 results
        response = f"I found {len(self.search_results)} option(s) near you:\n\n"

        for i, provider in enumerate(self.search_results[:3], 1):
            response += f"{i}. {self.format_provider_info(provider, self.user_location)}"

        if len(self.search_results) > 3:
            response += f"...and {len(self.search_results) - 3} more options.\n\n"

        response += """Would you like to:
• Compare options (type "compare")
• Get more details about a specific option (type the number)
• See more results (type "more")
• Start a new search (type "new")

What would you like to do?"""

        return response

    def _handle_results_interaction(self, message: str) -> str:
        """Handle user interaction with search results"""
        if message in ["compare", "comparison"]:
            self.state = ChatState.COMPARE_OPTIONS
            return self._show_comparison()
        elif message == "more":
            return self._show_more_results()
        elif message == "new":
            self._reset_conversation()
            return self._handle_welcome()
        elif message.isdigit():
            option_num = int(message) - 1
            if 0 <= option_num < len(self.search_results):
                self.current_options = [self.search_results[option_num]]
                self.state = ChatState.GET_MORE_DETAILS
                return self._show_detailed_info(self.search_results[option_num])
            else:
                return "Invalid option number. Please choose a valid number from the list."
        else:
            return """Please choose:
• "compare" to compare options
• "more" to see additional results
• A number (1, 2, 3, etc.) for more details about that option
• "new" to start a new search"""

    def _show_comparison(self) -> str:
        """Show comparison of options"""
        if len(self.search_results) < 2:
            return "I need at least 2 options to compare. Let me show you the available options instead.\n\n" + self._handle_budget_input("any")

        response = "📊 Comparing Options:\n\n"

        for i, provider in enumerate(self.search_results[:3], 1):
            distance = self.user_location.distance_to(provider.location)
            budget_cat = self.get_budget_category(provider.price_range)

            response += f"""Option {i}: {provider.name}
• Price: ${provider.price_range[0]}-${provider.price_range[1]} ({budget_cat.value})
• Distance: {distance:.1f} km
• Rating: {provider.rating}/5 ⭐
• Accessibility: {provider.accessibility.replace('_', ' ').title()}

"""

        response += """Which option interests you most? (type the number)
Or type "back" to return to results."""

        return response

    def _show_more_results(self) -> str:
        """Show additional search results"""
        if len(self.search_results) <= 3:
            return "No more results to show. Type 'compare' to compare options or 'new' for a new search."

        response = "Here are more options:\n\n"

        for i, provider in enumerate(self.search_results[3:6], 4):
            response += f"{i - 3}. {self.format_provider_info(provider, self.user_location)}"

        response += "\nType a number for more details, 'compare' to compare, or 'new' for a new search."
        return response

    def _show_detailed_info(self, provider: ServiceProvider) -> str:
        """Show detailed information about a provider"""
        distance = self.user_location.distance_to(provider.location)
        budget_cat = self.get_budget_category(provider.price_range)

        accessibility_guide = ACCESSIBILITY_GUIDES[provider.accessibility].format(distance=f"{distance:.1f}")

        response = RESPONSE_TEMPLATES["detailed_info"].format(
            name=provider.name,
            min_price=provider.price_range[0],
            max_price=provider.price_range[1],
            budget_cat=budget_cat.value,
            rating=provider.rating,
            area=provider.location.name,
            landmark=provider.location.landmark,
            distance=f"{distance:.1f}",
            accessibility_guide=accessibility_guide,
            hours=provider.operating_hours,
            contact=provider.contact_info,
            description=provider.description
        )

        self.state = ChatState.CONFIRM_CHOICE
        return response

    def _handle_comparison(self, message: str) -> str:
        """Handle comparison interactions"""
        if message == "back":
            self.state = ChatState.SHOW_RESULTS
            return self._handle_results_interaction("")

        if message.isdigit():
            option_num = int(message) - 1
            if 0 <= option_num < len(self.search_results):
                self.current_options = [self.search_results[option_num]]
                self.state = ChatState.GET_MORE_DETAILS
                return self._show_detailed_info(self.search_results[option_num])

        return "Please type a valid option number or 'back' to return."

    def _handle_more_details(self, message: str) -> str:
        """Handle detailed view interactions"""
        if message == "call":
            provider = self.current_options[0]
            return f"""📞 Calling {provider.name} at {provider.contact_info}...

(In a real implementation, this would initiate a phone call)

Type "back" to return to details or "new" for a new search."""
        elif message == "directions":
            provider = self.current_options[0]
            maps_link = f"https://www.google.com/maps/dir/?api=1&destination={provider.location.latitude},{provider.location.longitude}"

            return f"""🗺️ Directions to {provider.name}:

📍 Location: {provider.location.name}, near {provider.location.landmark}
📏 Distance: {self.user_location.distance_to(provider.location):.1f} km from your location
🚶 Accessibility: {provider.accessibility.replace('_', ' ').title()}

🗺️ *Google Maps Link:*
{maps_link}

📱 *WhatsApp Location:* I'll send the exact location pin to your WhatsApp!

Type "back" to return to details or "new" for a new search."""
        elif message in ["compare", "back"]:
            self.state = ChatState.SHOW_RESULTS
            return self._handle_results_interaction("")
        elif message == "new":
            self._reset_conversation()
            return self._handle_welcome()

        return """Please choose:
• "call" to call the provider
• "directions" to get directions
• "compare" to compare with other options
• "back" to return to results
• "new" for a new search"""

    def _handle_confirmation(self, message: str) -> str:
        """Handle final confirmation"""
        return self._handle_more_details(message)

    def _reset_conversation(self):
        """Reset conversation state"""
        self.state = ChatState.WELCOME
        self.user_location = None
        self.selected_service = None
        self.budget_range = None
        self.search_results = []
        self.current_options = []


def main():
    """Main function to run the chatbot in console mode"""
    chatbot = LocationBasedChatbot()

    print("🤖 Tanzania Location-Based Service Search Chatbot")
    print("=" * 50)
    print("Console Mode - Type 'quit' to exit")
    print("For WhatsApp mode, run: python -m ghala_whatsapp")
    print("=" * 50)

    while True:
        if chatbot.state == ChatState.WELCOME:
            print(chatbot.process_message(""))
        else:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye! Thanks for using our service finder.")
                break
            response = chatbot.process_message(user_input)
            print(f"\n🤖 Bot: {response}")


def run_whatsapp_server():
    """Run the chatbot in WhatsApp mode using Meta WhatsApp Business API"""
    from env_config import Config

    print("🇹🇿 Tanzania Service Chatbot - Meta WhatsApp Business API Mode")
    print("=" * 60)

    if not Config.is_whatsapp_configured():
        Config.print_setup_instructions()
        print("\n❌ WhatsApp not configured. Running in console mode instead...")
        print()
        main()
        return

    try:
        from ghala_whatsapp import MetaWhatsAppIntegration

        # Test connection
        print("🧪 Testing Meta WhatsApp API connection...")
        whatsapp = MetaWhatsAppIntegration(
            access_token=Config.WHATSAPP_ACCESS_TOKEN,
            phone_number_id=Config.WHATSAPP_PHONE_NUMBER_ID,
            waba_id=Config.WHATSAPP_WABA_ID,
            webhook_verify_token=Config.WHATSAPP_WEBHOOK_TOKEN
        )

        if whatsapp.test_connection():
            print("✅ Meta WhatsApp API connection successful!")
        else:
            print("❌ Meta WhatsApp API connection failed. Check your credentials.")
            return

        # Run server
        whatsapp.run_webhook_server(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG
        )

    except Exception as e:
        print(f"❌ Error starting WhatsApp server: {e}")
        print("Falling back to console mode...")
        main()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--whatsapp":
        run_whatsapp_server()
    else:
        main()


if __name__ == "__main__":
    main()
