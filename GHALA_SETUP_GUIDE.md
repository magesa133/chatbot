# 🇹🇿 Ghala WhatsApp Integration - Complete Setup Guide

## 📱 Add This Webhook Template to Ghala Platform

### Step 1: Sign up for Ghala
1. Visit [https://dev.ghala.io/](https://dev.ghala.io/)
2. Create a free account
3. Complete verification process
4. Access your dashboard

### Step 2: Create WhatsApp App
1. In Ghala dashboard, go to "Apps" section
2. Click "Create New App"
3. Select "WhatsApp Business API"
4. Fill in your business details

### Step 3: Get API Credentials
After creating the app, you'll get:
- **App ID**: `your_ghala_app_id`
- **App Secret**: `your_ghala_app_secret`

### Step 4: Configure Webhook
In your Ghala app settings:

#### Webhook URL
```
https://your-domain.com/webhook
```

#### Verify Token
```
tanzania_service_bot_verify_token
```

#### Webhook Events
Subscribe to these events:
- ✅ `messages` - Incoming messages
- ✅ `message_deliveries` - Delivery confirmations
- ✅ `message_reads` - Read receipts

## 🔧 Code Template for Ghala Platform

### Option 1: Use Our Ready Template

Copy the `ghala_webhook_template.py` file to your server and deploy it:

```bash
# Deploy the Ghala bot
./deploy_ghala.sh
```

### Option 2: Integrate with Your Existing Code

Add this webhook handler to your existing Flask/Django application:

```python
# Add to your Flask routes
@app.route('/webhook', methods=['GET'])
def verify_ghala_webhook():
    """Ghala webhook verification"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == 'tanzania_service_bot_verify_token':
        return challenge, 200
    return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def handle_ghala_message():
    """Handle Ghala WhatsApp messages"""
    data = request.get_json()

    if data and 'messages' in data:
        for message in data['messages']:
            # Process your messages here
            sender_id = message.get('from')
            message_type = message.get('type')

            if message_type == 'text':
                text = message.get('text', {}).get('body', '')
                # Handle text message
                send_ghala_message(sender_id, f"You said: {text}")
            elif message_type == 'location':
                # Handle location sharing
                pass

    return jsonify({'status': 'success'}), 200

def send_ghala_message(recipient_id, message):
    """Send message via Ghala API"""
    import requests

    payload = {
        "to": recipient_id,
        "type": "text",
        "text": {"body": message}
    }

    headers = {
        "Authorization": f"Bearer YOUR_APP_SECRET",
        "Content-Type": "application/json",
        "X-App-Id": "YOUR_APP_ID"
    }

    response = requests.post(
        "https://dev.ghala.io/api/v1/messages",
        json=payload,
        headers=headers
    )

    return response.status_code == 200
```

## 📋 Ghala API Message Formats

### Send Text Message
```json
POST https://dev.ghala.io/api/v1/messages
Headers:
  Authorization: Bearer {APP_SECRET}
  Content-Type: application/json
  X-App-Id: {APP_ID}

Body:
{
  "to": "255XXXXXXXXX",
  "type": "text",
  "text": {
    "body": "Hello from Tanzania Service Bot! 🇹🇿"
  }
}
```

### Send Location Message
```json
POST https://dev.ghala.io/api/v1/messages
Headers:
  Authorization: Bearer {APP_SECRET}
  Content-Type: application/json
  X-App-Id: {APP_ID}

Body:
{
  "to": "255XXXXXXXXX",
  "type": "location",
  "location": {
    "latitude": "-6.7572",
    "longitude": "39.2763",
    "name": "Restaurant Name",
    "address": "Masaki, Dar es Salaam"
  }
}
```

### Receive Messages (Webhook)
```json
{
  "messages": [
    {
      "id": "message_id",
      "from": "255XXXXXXXXX",
      "type": "text",
      "timestamp": "1640995200",
      "text": {
        "body": "Hello bot!"
      }
    }
  ]
}
```

### Receive Location (Webhook)
```json
{
  "messages": [
    {
      "id": "message_id",
      "from": "255XXXXXXXXX",
      "type": "location",
      "timestamp": "1640995200",
      "location": {
        "latitude": -6.7572,
        "longitude": 39.2763
      }
    }
  ]
}
```

## 🧪 Testing Your Ghala Integration

### Test Webhook Verification
```bash
curl "https://your-domain.com/webhook?hub.mode=subscribe&hub.verify_token=tanzania_service_bot_verify_token&hub.challenge=test123"
# Should return: test123
```

### Test Health Check
```bash
curl https://your-domain.com/health
# Should return JSON with status: healthy
```

### Send Test Message
```bash
curl -X POST https://your-domain.com/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "id": "test_123",
      "from": "255XXXXXXXXX",
      "type": "text",
      "text": {"body": "Hello"}
    }]
  }'
```

## 🚀 Production Deployment

### Server Requirements
- Python 3.7+
- Flask
- Public HTTPS URL (required by WhatsApp)
- Stable internet connection

### Environment Variables
```bash
export GHALA_APP_ID='your_production_app_id'
export GHALA_APP_SECRET='your_production_app_secret'
export FLASK_ENV='production'
```

### Using Docker (Recommended)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ghala_webhook_template.py .
EXPOSE 5000

CMD ["python", "ghala_webhook_template.py"]
```

### Using Railway/Render/Heroku
1. Deploy the `ghala_webhook_template.py` file
2. Set environment variables in dashboard
3. Use the provided domain as webhook URL
4. Configure webhook URL in Ghala dashboard

## 🔧 Troubleshooting

### Webhook Verification Fails
- Check verify token matches exactly
- Ensure webhook URL is HTTPS
- Verify server is running and accessible

### Messages Not Received
- Check webhook URL is correctly set in Ghala
- Verify app is active in Ghala dashboard
- Check server logs for errors

### Messages Not Sent
- Verify App ID and App Secret are correct
- Check recipient phone number format (+255XXXXXXXXX)
- Ensure app has sending permissions

### Location Messages Not Working
- Check latitude/longitude are strings, not numbers
- Verify coordinates are valid
- Test with text messages first

## 📞 Support

### Ghala Support
- **Website**: [https://dev.ghala.io/](https://dev.ghala.io/)
- **Documentation**: Check their API docs
- **Contact**: Use their support channels

### Template Issues
- Check server logs: `tail -f /var/log/ghala-bot.log`
- Verify all environment variables are set
- Test with simple text messages first

## 🎯 Tanzania-Specific Features

The template includes:
- ✅ **Swahili greetings** ("Habari!")
- ✅ **Tanzania locations** (Masaki, Kinondoni, etc.)
- ✅ **TZS currency** pricing
- ✅ **Local service categories** (karakana, kliniki, kinyozi)
- ✅ **Regional context** and knowledge

---

**🎉 Your Ghala WhatsApp Tanzania Service Bot is ready!**

**Next steps:**
1. Deploy the template to your server
2. Configure webhook in Ghala dashboard
3. Test with real WhatsApp messages
4. Customize responses for your specific services

🇹🇿 **Tanzanian users can now chat with your AI service bot!** 🤖📱✨
