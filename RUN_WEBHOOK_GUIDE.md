# 🚀 Running the Tanzania Service Chatbot with WhatsApp Webhooks

## Overview

Your chatbot now supports **live WhatsApp messaging** through webhooks. Users can send messages to your WhatsApp Business number and receive instant responses with service recommendations.

## 📋 Prerequisites

### 1. WhatsApp Business Account
Choose your provider:
- **Ghala** (Recommended for Tanzania): https://dev.ghala.io/
- **Meta WhatsApp Business API**: https://developers.facebook.com/

### 2. Environment Setup
```bash
# Activate virtual environment
cd /home/magesa/MAGESA/chatbot
source ../../tanzania_chatbot_env/bin/activate

# Set credentials
export WHATSAPP_PROVIDER='ghala'  # or 'meta'
export GHALA_APP_ID='your_app_id'
export GHALA_APP_SECRET='your_app_secret'
# OR for Meta:
export WHATSAPP_ACCESS_TOKEN='your_token'
export WHATSAPP_PHONE_NUMBER_ID='your_phone_id'
```

## 🚀 Running the Webhook Server

### Option 1: Standalone Webhook Server (Recommended)
```bash
cd /home/magesa/MAGESA/chatbot
python webhook_server.py
```

**What this provides:**
- ✅ Webhook verification endpoint
- ✅ Message handling for both Meta & Ghala
- ✅ Health check endpoint
- ✅ Automatic response generation
- ✅ Error handling and logging

### Option 2: Full Chatbot with WhatsApp
```bash
cd /home/magesa/MAGESA/chatbot
python main.py --whatsapp
```

### Option 3: Quick Start Script
```bash
cd /home/magesa/MAGESA/chatbot
./run_whatsapp.sh
```

## 🌐 Webhook Configuration

### For Ghala Dashboard:
1. **Login** to https://dev.ghala.io/dashboard
2. **Go to** your WhatsApp app settings
3. **Set Webhook URL**: `https://your-domain.com/webhook`
4. **Set Verify Token**: `tanzania_service_bot_ghala`
5. **Subscribe** to `messages` events

### For Meta WhatsApp:
1. **Login** to https://developers.facebook.com/
2. **Go to** your WhatsApp app settings
3. **Set Webhook URL**: `https://your-domain.com/webhook`
4. **Set Verify Token**: `tanzania_service_bot_2024`
5. **Subscribe** to `messages` events

## 🧪 Testing Your Webhook

### 1. Test Health Check
```bash
curl http://localhost:5000/health
# Should return: {"status": "healthy", "provider": "ghala", ...}
```

### 2. Test Webhook Verification
```bash
curl "http://localhost:5000/webhook?hub.mode=subscribe&hub.verify_token=tanzania_service_bot_ghala&hub.challenge=test123"
# Should return: test123
```

### 3. Test Message Handling
```bash
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "id": "test_123",
      "from": "255XXXXXXXXX",
      "type": "text",
      "text": {"body": "hello"}
    }]
  }'
# Should return: {"status": "success"}
```

## 🌍 Production Deployment

### Using a VPS/Cloud Server
```bash
# 1. Upload your code to server
scp -r /home/magesa/MAGESA/chatbot user@your-server:/path/to/app/

# 2. Install dependencies
ssh user@your-server
cd /path/to/app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Set environment variables
export WHATSAPP_PROVIDER='ghala'
export GHALA_APP_ID='your_production_app_id'
export GHALA_APP_SECRET='your_production_app_secret'

# 4. Run with production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 webhook_server:app
```

### Using Docker
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "webhook_server.py"]
```

```bash
# Build and run
docker build -t tanzania-chatbot .
docker run -p 5000:5000 -e GHALA_APP_ID=your_id -e GHALA_APP_SECRET=your_secret tanzania-chatbot
```

### Using Railway/Render/Heroku
1. **Deploy** the `webhook_server.py` file
2. **Set environment variables** in dashboard
3. **Use the provided domain** as webhook URL
4. **Configure webhook** in your WhatsApp provider dashboard

## 🔧 Webhook URLs for Different Providers

### Ghala Format:
```json
POST https://your-domain.com/webhook
Content-Type: application/json
Authorization: Bearer your_app_secret

{
  "messages": [{
    "id": "msg_123",
    "from": "255XXXXXXXXX",
    "type": "text",
    "text": {"body": "Hello"}
  }]
}
```

### Meta Format:
```json
POST https://your-domain.com/webhook
Content-Type: application/json

{
  "object": "whatsapp_business_account",
  "entry": [{
    "changes": [{
      "value": {
        "messages": [{
          "id": "msg_123",
          "from": "255XXXXXXXXX",
          "type": "text",
          "text": {"body": "Hello"}
        }]
      }
    }]
  }]
}
```

## 📱 Sample User Conversation

```
User: Hi
Bot: 🇹🇿 Tanzania Service Finder
     Habari! I'm your AI assistant...
     Send your location or tell me what you need!

User: restaurants
Bot: 🍽️ Popular Restaurants in Dar es Salaam
     🏪 Beach Banda - Oyster Bay
        💰 TZS 15,000-45,000
        ⭐ 4.2/5 stars
     Reply with a name for directions!

User: directions to Beach Banda
Bot: 🗺️ Directions to Beach Banda
     📍 Address: Oyster Bay, Dar es Salaam
     📏 Distance: 2.3 km
     💰 Estimated cost: TZS 25,000-45,000
     [Location pin sent automatically]
```

## 🔍 Monitoring & Debugging

### View Logs
```bash
# Server logs show all webhook activity
tail -f /var/log/tanzania-webhook.log
```

### Check Message Status
```bash
# Health endpoint shows server status
curl http://your-domain.com/health
```

### Test Individual Components
```bash
# Test Ghala SDK
python example_ghala_usage.py

# Test template manager
python whatsapp_template_manager.py --list

# Test environment config
python -c "from env_config import Config; print(f'Configured: {Config.is_whatsapp_configured()}')"
```

## 🚨 Troubleshooting

### "Webhook verification failed"
- ✅ Check webhook token matches dashboard
- ✅ Verify URL is HTTPS (production)
- ✅ Ensure server is accessible

### "Messages not received"
- ✅ Check webhook URL is correct in dashboard
- ✅ Verify app has message permissions
- ✅ Check server logs for errors

### "Messages not sent"
- ✅ Validate API credentials
- ✅ Check phone number format (+255XXXXXXXXX)
- ✅ Verify API endpoints are correct

### Server Connection Issues
- ✅ Check firewall settings
- ✅ Verify port 5000 is open
- ✅ Test with local curl commands

## 🎯 Success Metrics

### Monitor These KPIs:
- ✅ **Message Delivery Rate**: % of sent messages delivered
- ✅ **Response Time**: Average time to respond
- ✅ **User Engagement**: Messages per user session
- ✅ **Service Requests**: Popular service categories
- ✅ **Location Accuracy**: Successful location processing

## 🔄 Scaling & Optimization

### For High Traffic:
- ✅ **Use Redis** for session storage
- ✅ **Implement rate limiting**
- ✅ **Add message queuing** (Celery/RabbitMQ)
- ✅ **Database integration** for analytics
- ✅ **Load balancing** across multiple servers

### Performance Tips:
- ✅ **Cache frequent responses**
- ✅ **Optimize OpenStreetMap queries**
- ✅ **Use async processing** for slow operations
- ✅ **Implement connection pooling**
- ✅ **Add monitoring dashboards**

## 📞 Support & Resources

### Ghala Support:
- **Dashboard**: https://dev.ghala.io/dashboard
- **Documentation**: Check API docs in dashboard
- **Contact**: Support channels in dashboard

### Meta Support:
- **Documentation**: https://developers.facebook.com/docs/whatsapp
- **Status Page**: https://developers.facebook.com/status
- **Support**: Developer support tickets

### Chatbot Resources:
- **GitHub**: Project repository
- **Logs**: `/var/log/tanzania-webhook.log`
- **Health**: `https://your-domain.com/health`

---

**🎉 Your Tanzania Service Chatbot is now running with live WhatsApp webhooks! Users can message your business number and get instant AI-powered service recommendations with real-time location data!**

**🇹🇿 Happy chatting! 🤖📱✨**
