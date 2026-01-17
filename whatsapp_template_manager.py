#!/usr/bin/env python3
"""
WhatsApp Template Manager for Tanzania Service Chatbot
Handles template creation, submission, and management for Meta WhatsApp Business API
"""

import json
import requests
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppTemplateManager:
    """Manages WhatsApp message templates for Meta Business API"""

    def __init__(self, access_token: str = None, waba_id: str = None):
        """
        Initialize template manager

        Args:
            access_token: Meta WhatsApp API access token
            waba_id: WhatsApp Business Account ID
        """
        self.access_token = access_token or "YOUR_ACCESS_TOKEN"
        self.waba_id = waba_id or "YOUR_WABA_ID"
        self.base_url = f"https://graph.facebook.com/v18.0/{self.waba_id}"

        # Load templates
        with open('whatsapp_templates.json', 'r') as f:
            self.templates = json.load(f)['tanzania_service_templates']

    def submit_template(self, template_name: str) -> Dict[str, Any]:
        """
        Submit a template to WhatsApp for approval

        Args:
            template_name: Name of template to submit

        Returns:
            API response
        """
        template = self._get_template_by_name(template_name)
        if not template:
            return {"error": f"Template '{template_name}' not found"}

        url = f"{self.base_url}/message_templates"

        payload = {
            "name": template["template_name"],
            "category": template["category"],
            "language": template["language"],
            "components": []
        }

        # Add header if present
        if "header" in template and template["header"]:
            payload["components"].append({
                "type": "HEADER",
                "format": "TEXT",
                "text": template["header"]
            })

        # Add body (required)
        payload["components"].append({
            "type": "BODY",
            "text": template["body"]
        })

        # Add footer if present
        if "footer" in template and template["footer"]:
            payload["components"].append({
                "type": "FOOTER",
                "text": template["footer"]
            })

        # Add buttons if present
        if "buttons" in template and template["buttons"]:
            button_components = []
            for button in template["buttons"]:
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
                payload["components"].append({
                    "type": "BUTTONS",
                    "buttons": button_components
                })

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()

            if response.status_code == 200:
                logger.info(f"✅ Template '{template_name}' submitted successfully")
                logger.info(f"Template ID: {result.get('id')}")
                logger.info(f"Status: {result.get('status')}")
            else:
                logger.error(f"❌ Failed to submit template: {response.status_code}")
                logger.error(f"Response: {result}")

            return result

        except Exception as e:
            logger.error(f"❌ Error submitting template: {e}")
            return {"error": str(e)}

    def list_templates(self, status: str = None) -> List[Dict[str, Any]]:
        """
        List existing templates

        Args:
            status: Filter by status (APPROVED, PENDING, REJECTED, etc.)

        Returns:
            List of templates
        """
        url = f"{self.base_url}/message_templates"
        params = {}
        if status:
            params["status"] = status

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                logger.error(f"Failed to list templates: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return []

    def delete_template(self, template_name: str) -> bool:
        """
        Delete a template

        Args:
            template_name: Name of template to delete

        Returns:
            Success status
        """
        # First get template ID
        templates = self.list_templates()
        template_id = None

        for template in templates:
            if template.get("name") == template_name:
                template_id = template.get("id")
                break

        if not template_id:
            logger.error(f"Template '{template_name}' not found")
            return False

        url = f"{self.base_url}/message_templates/{template_id}"

        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.delete(url, headers=headers)
            if response.status_code == 200:
                logger.info(f"✅ Template '{template_name}' deleted successfully")
                return True
            else:
                logger.error(f"❌ Failed to delete template: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Error deleting template: {e}")
            return False

    def _get_template_by_name(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get template by name"""
        for template in self.templates:
            if template["template_name"] == template_name:
                return template
        return None

    def get_template_form_data(self, template_name: str) -> Dict[str, Any]:
        """
        Get template data formatted for Meta's template creation form

        Returns data that can be directly copied into the WhatsApp template form
        """
        template = self._get_template_by_name(template_name)
        if not template:
            return {"error": f"Template '{template_name}' not found"}

        return {
            "whatsapp_account": "YOUR_PHONE_NUMBER_ID",
            "template_name": template["template_name"],
            "category": template["category"],
            "language": template["language"],
            "header": template.get("header", ""),
            "body": template["body"],
            "footer": template.get("footer", ""),
            "buttons": template.get("buttons", [])
        }

    def print_template_form(self, template_name: str):
        """Print template in a format that can be copied to Meta's form"""
        data = self.get_template_form_data(template_name)

        if "error" in data:
            print(f"❌ {data['error']}")
            return

        print("📋 Copy this data into Meta WhatsApp Template Form:")
        print("=" * 50)
        print(f"WhatsApp Account: {data['whatsapp_account']}")
        print(f"Template Name: {data['template_name']}")
        print(f"Category: {data['category']}")
        print(f"Language: {data['language']}")
        print(f"Header: {data['header']}")
        print(f"Body: {data['body']}")
        print(f"Footer: {data['footer']}")

        if data['buttons']:
            print("Buttons:")
            for i, button in enumerate(data['buttons'], 1):
                print(f"  {i}. Type: {button['type']}, Text: {button['text']}")
                if 'url' in button:
                    print(f"     URL: {button['url']}")
                if 'phone_number' in button:
                    print(f"     Phone: {button['phone_number']}")

        print("=" * 50)


def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Template Manager')
    parser.add_argument('--access-token', help='Meta WhatsApp Access Token')
    parser.add_argument('--waba-id', help='WhatsApp Business Account ID')
    parser.add_argument('--submit', help='Submit template by name')
    parser.add_argument('--list', action='store_true', help='List all templates')
    parser.add_argument('--delete', help='Delete template by name')
    parser.add_argument('--form', help='Show template form data for copying')
    parser.add_argument('--template', help='Template name for operations')

    args = parser.parse_args()

    # Initialize manager
    manager = WhatsAppTemplateManager(
        access_token=args.access_token,
        waba_id=args.waba_id
    )

    if args.list:
        print("📋 Existing Templates:")
        templates = manager.list_templates()
        for template in templates:
            status = template.get('status', 'UNKNOWN')
            print(f"• {template['name']} - {status}")

    elif args.submit:
        if not args.access_token or not args.waba_id:
            print("❌ Error: --access-token and --waba-id required for submission")
            return

        result = manager.submit_template(args.submit)
        print(f"Submission result: {result}")

    elif args.delete:
        if not args.access_token or not args.waba_id:
            print("❌ Error: --access-token and --waba-id required for deletion")
            return

        success = manager.delete_template(args.delete)
        print(f"Delete result: {'Success' if success else 'Failed'}")

    elif args.form:
        manager.print_template_form(args.form)

    else:
        print("🇹🇿 WhatsApp Template Manager for Tanzania Service Chatbot")
        print()
        print("Available templates:")
        for template in manager.templates:
            print(f"• {template['template_name']} - {template['category']}")
        print()
        print("Usage examples:")
        print("  python whatsapp_template_manager.py --form tanzania_service_welcome")
        print("  python whatsapp_template_manager.py --list")
        print("  python whatsapp_template_manager.py --submit service_recommendations --access-token YOUR_TOKEN --waba-id YOUR_WABA_ID")


if __name__ == "__main__":
    main()
