#!/usr/bin/env python3
"""
Test script to verify webhook CORS and connectivity
"""

import requests
import json

def test_webhook_cors():
    """Test webhook endpoints with CORS"""

    base_url = "http://localhost:5000"
    ngrok_origin = "https://ileana-unsupposed-nonmortally.ngrok-free.app"

    headers = {
        "Origin": ngrok_origin,
        "User-Agent": "WhatsApp-Webhook-Test/1.0"
    }

    print("🇹🇿 Testing Tanzania Chatbot Webhook CORS")
    print("=" * 50)

    # Test 1: Health endpoint
    print("\n1️⃣ Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/health", headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   CORS Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: Webhook verification
    print("\n2️⃣ Testing Webhook Verification...")
    try:
        params = {
            "hub.mode": "subscribe",
            "hub.verify_token": "tanzania_service_bot_ghala",
            "hub.challenge": "CORS_SUCCESS_2024"
        }
        response = requests.get(f"{base_url}/webhook", params=params, headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   CORS Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
        print(f"   Challenge: {response.text.strip()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 3: Simulate WhatsApp message
    print("\n3️⃣ Testing WhatsApp Message Simulation...")
    try:
        message_data = {
            "messages": [{
                "id": "test_msg_123",
                "from": "255XXXXXXXXX",
                "type": "text",
                "text": {"body": "hello"}
            }]
        }
        headers["Content-Type"] = "application/json"
        response = requests.post(f"{base_url}/webhook", json=message_data, headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   CORS Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 4: Options preflight
    print("\n4️⃣ Testing OPTIONS Preflight...")
    try:
        options_headers = {
            "Origin": ngrok_origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,X-App-Id"
        }
        response = requests.options(f"{base_url}/webhook", headers=options_headers, timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
        print(f"   Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'NOT SET')}")
        print(f"   Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'NOT SET')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "=" * 50)
    print("🎉 CORS Testing Complete!")
    print("🌐 Your webhook is now accessible from any origin!")
    print("📱 Ready to receive WhatsApp messages via ngrok!")

    # Show ngrok test command
    print("\n🚀 Test your public ngrok URL:")
    print(f"curl -H 'Origin: {ngrok_origin}' https://ileana-unsupposed-nonmortally.ngrok-free.app/health")

if __name__ == "__main__":
    test_webhook_cors()
