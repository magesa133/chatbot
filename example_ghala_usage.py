#!/usr/bin/env python3
"""
Example usage of Ghala WhatsApp SDK
Shows how to send messages using the service_recommendations template
"""

from ghala_sdk import create_ghala_client, MessageResponse

def main():
    """Example of using Ghala SDK to send service recommendations"""

    # Initialize Ghala client (replace with your credentials)
    client = create_ghala_client(
        app_id="your_ghala_app_id",
        app_secret="your_ghala_app_secret"
    )

    # Test connection
    print("Testing Ghala connection...")
    test_result = client.test_connection()
    if not test_result.success:
        print(f"❌ Connection failed: {test_result.error}")
        return

    print("✅ Connected to Ghala API")

    # Example service recommendation
    recipient_number = "255XXXXXXXXX"  # Tanzanian number in E.164 format

    # Send service recommendation using template
    print(f"Sending service recommendation to {recipient_number}...")

    result = client.send_service_recommendation(
        to=recipient_number,
        user_name="John Doe",
        location="Masaki, Dar es Salaam",
        service_details="🏪 Beach Banda Restaurant\n   📍 Excellent seafood cuisine\n   ⭐ Highly rated by locals",
        cost="25,000 - 45,000",
        distance="1.2"
    )

    if result.success:
        print("✅ Message sent successfully!"        if result.message_id:
            print(f"Message ID: {result.message_id}")
    else:
        print(f"❌ Failed to send message: {result.error}")

    # Example of sending a regular text message
    print(f"Sending follow-up text message...")

    text_result = client.send_text_message(
        to=recipient_number,
        text="Thank you for using Tanzania Services! 🇹🇿\n\nFor more recommendations, just let us know what you're looking for."
    )

    if text_result.success:
        print("✅ Follow-up message sent!")
    else:
        print(f"❌ Follow-up message failed: {text_result.error}")

if __name__ == "__main__":
    print("🇹🇿 Ghala WhatsApp SDK Example")
    print("=" * 40)

    # Check if credentials are set
    import os
    if not os.getenv('GHALA_APP_ID') or not os.getenv('GHALA_APP_SECRET'):
        print("⚠️  Please set your Ghala credentials:")
        print("   export GHALA_APP_ID='your_app_id'")
        print("   export GHALA_APP_SECRET='your_app_secret'")
        print()
        print("For testing, you can run this script with dummy credentials")
        print("but messages won't actually be sent.")
        print()

    main()
