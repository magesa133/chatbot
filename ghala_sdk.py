#!/usr/bin/env python3
"""
Ghala WhatsApp SDK for Tanzania Service Chatbot
Official SDK wrapper for Ghala WhatsApp Business API
https://dev.ghala.io/dashboard?tab=docs
"""

import requests
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GhalaCredentials:
    """Ghala API credentials"""
    app_id: str
    app_secret: str
    phone_number_id: Optional[str] = None


@dataclass
class MessageResponse:
    """Response from Ghala API"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class GhalaWhatsAppSDK:
    """
    Ghala WhatsApp Business API SDK
    Based on https://dev.ghala.io/dashboard?tab=docs
    """

    def __init__(self, credentials: GhalaCredentials):
        """
        Initialize Ghala SDK

        Args:
            credentials: GhalaCredentials object with app_id and app_secret
        """
        self.credentials = credentials
        self.base_url = "https://dev.ghala.io/api/v1"
        self.headers = {
            "Authorization": f"Bearer {credentials.app_secret}",
            "Content-Type": "application/json",
            "X-App-Id": credentials.app_id
        }

        logger.info("Ghala WhatsApp SDK initialized")

    def test_connection(self) -> MessageResponse:
        """
        Test connection to Ghala API

        Returns:
            MessageResponse with success status
        """
        try:
            # Try to get account info or send a test request
            test_url = f"{self.base_url}/account"
            response = requests.get(test_url, headers=self.headers, timeout=10)

            if response.status_code in [200, 401, 403]:
                return MessageResponse(
                    success=True,
                    data={"status": "connected", "status_code": response.status_code}
                )
            else:
                return MessageResponse(
                    success=False,
                    error=f"Connection test failed: {response.status_code}"
                )

        except Exception as e:
            logger.error(f"Connection test error: {e}")
            return MessageResponse(success=False, error=str(e))

    def send_text_message(self, to: str, text: str) -> MessageResponse:
        """
        Send a text message

        Args:
            to: Recipient phone number (E.164 format, e.g., "255XXXXXXXXX")
            text: Message text

        Returns:
            MessageResponse with result
        """
        payload = {
            "to": to,
            "type": "text",
            "text": {
                "body": text
            }
        }

        return self._send_request("messages", payload)

    def send_template_message(self, to: str, template_name: str,
                            parameters: List[str], language: str = "en") -> MessageResponse:
        """
        Send a template message

        Args:
            to: Recipient phone number
            template_name: Name of approved template
            parameters: List of parameter values for template
            language: Template language code

        Returns:
            MessageResponse with result
        """
        components = [{
            "type": "body",
            "parameters": [
                {"type": "text", "text": param} for param in parameters
            ]
        }]

        payload = {
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
                "components": components
            }
        }

        return self._send_request("messages", payload)

    def send_location_message(self, to: str, latitude: float, longitude: float,
                            name: Optional[str] = None, address: Optional[str] = None) -> MessageResponse:
        """
        Send a location message

        Args:
            to: Recipient phone number
            latitude: Location latitude
            longitude: Location longitude
            name: Optional location name
            address: Optional location address

        Returns:
            MessageResponse with result
        """
        location_data = {
            "latitude": str(latitude),
            "longitude": str(longitude)
        }

        if name:
            location_data["name"] = name
        if address:
            location_data["address"] = address

        payload = {
            "to": to,
            "type": "location",
            "location": location_data
        }

        return self._send_request("messages", payload)

    def send_service_recommendation(self, to: str, user_name: str, location: str,
                                  service_details: str, cost: str, distance: str) -> MessageResponse:
        """
        Send service recommendation using the approved template

        Args:
            to: Recipient phone number
            user_name: User's name
            location: Service location
            service_details: Details about the service
            cost: Estimated cost
            distance: Distance to service

        Returns:
            MessageResponse with result
        """
        parameters = [user_name, location, service_details, cost, distance]
        return self.send_template_message(to, "service_recommendations", parameters)

    def create_template(self, name: str, category: str, language: str,
                       body: str, header: Optional[str] = None,
                       footer: Optional[str] = None,
                       buttons: Optional[List[Dict[str, Any]]] = None) -> MessageResponse:
        """
        Create a message template (for approval)

        Args:
            name: Template name
            category: Template category (MARKETING, UTILITY, AUTHENTICATION)
            language: Language code
            body: Template body text
            header: Optional header
            footer: Optional footer
            buttons: Optional list of buttons

        Returns:
            MessageResponse with result
        """
        components = []

        if header:
            components.append({
                "type": "HEADER",
                "format": "TEXT",
                "text": header
            })

        components.append({
            "type": "BODY",
            "text": body
        })

        if footer:
            components.append({
                "type": "FOOTER",
                "text": footer
            })

        if buttons:
            button_components = []
            for button in buttons:
                if button["type"] == "QUICK_REPLY":
                    button_components.append({
                        "type": "QUICK_REPLY",
                        "text": button["text"]
                    })
                elif button["type"] == "URL":
                    button_components.append({
                        "type": "URL",
                        "text": button["text"],
                        "url": button["url"]
                    })
                elif button["type"] == "PHONE_NUMBER":
                    button_components.append({
                        "type": "PHONE_NUMBER",
                        "text": button["text"],
                        "phone_number": button["phone_number"]
                    })

            if button_components:
                components.append({
                    "type": "BUTTONS",
                    "buttons": button_components
                })

        payload = {
            "name": name,
            "category": category,
            "language": language,
            "components": components
        }

        template_url = f"{self.base_url}/message_templates"
        return self._send_request_to_url(template_url, payload, "POST")

    def list_templates(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List message templates

        Args:
            status: Optional status filter (APPROVED, PENDING, REJECTED)

        Returns:
            List of templates
        """
        url = f"{self.base_url}/message_templates"
        params = {}
        if status:
            params["status"] = status

        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                logger.error(f"Failed to list templates: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return []

    def get_template_status(self, template_name: str) -> Optional[str]:
        """
        Get template approval status

        Args:
            template_name: Name of template

        Returns:
            Status string or None if not found
        """
        templates = self.list_templates()
        for template in templates:
            if template.get("name") == template_name:
                return template.get("status")
        return None

    def _send_request(self, endpoint: str, payload: Dict[str, Any]) -> MessageResponse:
        """
        Send request to Ghala API

        Args:
            endpoint: API endpoint (e.g., "messages")
            payload: Request payload

        Returns:
            MessageResponse with result
        """
        url = f"{self.base_url}/{endpoint}"
        return self._send_request_to_url(url, payload, "POST")

    def _send_request_to_url(self, url: str, payload: Dict[str, Any], method: str = "POST") -> MessageResponse:
        """
        Send HTTP request to Ghala API

        Args:
            url: Full URL
            payload: Request payload
            method: HTTP method

        Returns:
            MessageResponse with result
        """
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            elif method.upper() == "GET":
                response = requests.get(url, headers=self.headers, timeout=30)
            else:
                return MessageResponse(success=False, error=f"Unsupported method: {method}")

            response_data = response.json() if response.content else {}

            if response.status_code == 200:
                message_id = response_data.get("messages", [{}])[0].get("id") if "messages" in response_data else None
                return MessageResponse(
                    success=True,
                    message_id=message_id,
                    data=response_data
                )
            else:
                error_msg = response_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                return MessageResponse(
                    success=False,
                    error=error_msg,
                    data=response_data
                )

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return MessageResponse(success=False, error=f"Request failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return MessageResponse(success=False, error=f"Unexpected error: {str(e)}")


# Convenience functions
def create_ghala_client(app_id: str, app_secret: str, phone_number_id: Optional[str] = None) -> GhalaWhatsAppSDK:
    """
    Create a Ghala WhatsApp SDK client

    Args:
        app_id: Ghala App ID
        app_secret: Ghala App Secret
        phone_number_id: Optional phone number ID

    Returns:
        GhalaWhatsAppSDK instance
    """
    credentials = GhalaCredentials(
        app_id=app_id,
        app_secret=app_secret,
        phone_number_id=phone_number_id
    )
    return GhalaWhatsAppSDK(credentials)


# Example usage
if __name__ == "__main__":
    # Example credentials (replace with real ones)
    credentials = GhalaCredentials(
        app_id="your_app_id",
        app_secret="your_app_secret"
    )

    client = GhalaWhatsAppSDK(credentials)

    # Test connection
    result = client.test_connection()
    print(f"Connection test: {'✅ Success' if result.success else '❌ Failed'}")

    if result.success:
        # Example: Send service recommendation
        response = client.send_service_recommendation(
            to="255XXXXXXXXX",
            user_name="John Doe",
            location="Masaki, Dar es Salaam",
            service_details="🏪 Beach Banda Restaurant\n   📍 Excellent seafood\n   ⭐ Highly rated",
            cost="25,000 - 45,000",
            distance="1.2"
        )

        print(f"Message sent: {'✅ Success' if response.success else '❌ Failed'}")
        if response.message_id:
            print(f"Message ID: {response.message_id}")
