# 🇹🇿 WhatsApp Setup Guide - Tanzania Service Chatbot

## 📱 Enable WhatsApp Integration

Your Tanzania Service Chatbot now supports **direct WhatsApp messaging** using the **Meta WhatsApp Business API**. Users can chat with your bot directly on WhatsApp to find services in Tanzania!

## 🚀 Quick Setup (5 minutes)

### 1. Set up Meta WhatsApp Business API
1. Visit [developers.facebook.com](https://developers.facebook.com/)
2. Create a Meta Developer account
3. Create a new app and add WhatsApp product
4. Complete business verification
5. Get your WhatsApp Business API access

### 2. Get API Credentials
1. In your Meta app dashboard, go to WhatsApp settings
2. Copy your:
   - **Access Token** (temporary or permanent)
   - **Phone Number ID**
   - **WABA ID** (WhatsApp Business Account ID)
   - **Webhook Token** (create one for verification)

### 3. Set Environment Variables
```bash
# Open terminal and set credentials
export WHATSAPP_ACCESS_TOKEN='your_actual_access_token'
export WHATSAPP_PHONE_NUMBER_ID='your_actual_phone_number_id'
export WHATSAPP_WABA_ID='your_actual_waba_id'
export WHATSAPP_WEBHOOK_TOKEN='tanzania_service_bot_2024'
```

### 4. Configure Webhook in Meta Dashboard
1. In your Meta app dashboard, go to Webhooks section
2. Add webhook URL: `https://your-domain.com/webhook`
3. Set verify token: `tanzania_service_bot_2024`
4. Subscribe to `messages` event

### 5. For Local Testing (Optional)
```bash
# Install ngrok to expose local server
npm install -g ngrok
ngrok http 5000

# Copy the ngrok URL (e.g., https://abc123.ngrok.io)
# Use this URL in Meta dashboard as your webhook URL
```

### 6. Start WhatsApp Server
```bash
# Navigate to chatbot directory
cd /home/magesa/MAGESA/chatbot

# Run WhatsApp server
./run_whatsapp.sh
```

## 📋 Configuration Checklist

- ✅ Meta Developer account created
- ✅ WhatsApp Business API app created
- ✅ Business verification completed
- ✅ Access Token obtained
- ✅ Phone Number ID obtained
- ✅ WABA ID obtained
- ✅ Webhook token set
- ✅ Environment variables exported
- ✅ Webhook URL configured in Meta dashboard
- ✅ Server running on port 5000

## 🧪 Test Your Setup

### Test API Connection
```bash
# Test if credentials work
python main.py --whatsapp --test
```

### Test Webhook (Local)
```bash
# Check if server is running
curl http://localhost:5000/health
```

### Test WhatsApp Messages
1. Send WhatsApp message to your Ghala number: "Hi"
2. Bot should respond with welcome message
3. Try: "Masaki, Dar es Salaam"
4. Bot should ask for service type

## 💬 Sample WhatsApp Conversation

```
📱 User: Hi
🤖 Bot: 🇹🇿 Tanzania Service Finder
        Karibu! I'm your AI assistant for finding services in Tanzania.
        Send your location or ask me anything!

📱 User: Masaki
🤖 Bot: What service do you need?
        • Auto repair (karakana)
        • Medical clinic (kliniki)
        • Hair salon (kinyozi)
        • Restaurant (migahawa)
        • And more...

📱 User: restaurant
🤖 Bot: What's your budget range?
        Low-cost: Under 50,000 TZS
        Mid-range: 50,000-150,000 TZS
        Premium: Over 150,000 TZS

📱 User: mid-range
🤖 Bot: Found 48 restaurants near Masaki:
        1. 🏪 Beach Banda - 1.0km - TZS 5,000-25,000
        2. 🏪 Goong Restaurant - 3.5km - TZS 5,000-25,000
        [More options with directions...]
```

## 🌐 Production Deployment

### For Live Server
1. Deploy your code to a VPS/cloud server
2. Set environment variables permanently
3. Use your server's public URL as webhook
4. Configure Ghala dashboard with production webhook URL
5. Start server: `python main.py --whatsapp`

### Environment Variables (Permanent)
```bash
# Add to ~/.bashrc or server environment
echo 'export GHALA_APP_ID="your_app_id"' >> ~/.bashrc
echo 'export GHALA_APP_SECRET="your_app_secret"' >> ~/.bashrc
echo 'export GHALA_WEBHOOK_TOKEN="tanzania_service_bot"' >> ~/.bashrc
source ~/.bashrc
```

## 🔧 Troubleshooting

### "Ghala API connection failed"
- Check your App ID and App Secret
- Verify internet connection
- Try regenerating API credentials

### "Webhook verification failed"
- Ensure webhook token matches Meta dashboard settings
- Check webhook URL is accessible (HTTPS required for production)
- For local testing, use ngrok HTTPS URL

### No responses on WhatsApp
- Check server is running: `curl http://localhost:5000/health`
- Verify webhook URL and token in Meta dashboard
- Check that your phone number is connected to WhatsApp Business API
- Check server logs for errors

### Location not recognized
- Try sending GPS coordinates: "latitude,longitude"
- Use major landmarks: "Kariakoo", "Posta", "University"
- Send location via WhatsApp location sharing

## 📊 Webhook Endpoints

- `GET /webhook` - Ghala webhook verification
- `POST /webhook` - Incoming WhatsApp messages
- `GET /health` - Server health check
- `GET /` - Basic info page

## 🎯 Advanced Features

### Multi-language Support
The bot automatically detects and responds in context appropriate for Tanzania users.

### Location Intelligence
- OpenStreetMap integration for real addresses
- Distance calculations in kilometers
- Walking/public transport/vehicle recommendations

### Service Database
- Real businesses from OpenStreetMap
- Tanzania Shilling pricing
- Contact information and operating hours
- Service ratings and descriptions

## 📞 Support

### Meta WhatsApp Business API Support
- Documentation: [developers.facebook.com/docs/whatsapp](https://developers.facebook.com/docs/whatsapp)
- API Reference: [developers.facebook.com/docs/whatsapp/api](https://developers.facebook.com/docs/whatsapp/api)
- Status Page: [developers.facebook.com/status](https://developers.facebook.com/status)
- Support: Contact Meta Developer Support for account issues

## 📍 Location Messaging Features

### How Location Messages Work
When users ask for directions or service locations, the bot sends:

1. **WhatsApp Location Pin** 📍
   - Interactive map pin that users can tap
   - Opens directly in WhatsApp Maps
   - Shows exact GPS coordinates

2. **Google Maps Link** 🗺️
   - Clickable link for full navigation
   - Works on all devices
   - Provides turn-by-turn directions

### API Message Format
```json
{
  "messaging_product": "whatsapp",
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

### User Experience
```
User: directions
Bot: 🗺️ Directions to Beach Banda Restaurant:

📍 Location: Masaki, Dar es Salaam
📏 Distance: 1.2 km from your location
🚶 Accessibility: Walking distance

🗺️ Google Maps Link:
https://www.google.com/maps/dir/?api=1&destination=-6.7572,39.2763

[WhatsApp sends location pin automatically]
```

### Bot Issues
- Check server logs: `tail -f /var/log/tanzania-chatbot.log`
- Test with console mode: `./run_chatbot.sh`
- Verify OpenStreetMap connectivity

## 🚀 Next Steps

1. **Test thoroughly** with real WhatsApp messages
2. **Customize responses** for your specific use case
3. **Add more services** to the database
4. **Implement user feedback** collection
5. **Scale to multiple servers** if needed

---

**🎉 Your Tanzania WhatsApp Service Bot is ready!**

Users can now chat with your bot directly on WhatsApp to find services across Tanzania! 🇹🇿🤖📱
