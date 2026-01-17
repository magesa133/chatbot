#!/bin/bash
# Ghala WhatsApp Bot Deployment Script

echo "🇹🇿 Ghala WhatsApp Tanzania Service Bot - Deployment"
echo "==================================================="

# Check if we're in the right directory
if [ ! -f "ghala_webhook_template.py" ]; then
    echo "❌ Error: ghala_webhook_template.py not found in current directory"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.7+"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "ghala_env" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv ghala_env
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source ghala_env/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q flask requests

# Check if credentials are set
echo ""
echo "🔑 Ghala Credentials Check:"
if [ -z "$GHALA_APP_ID" ]; then
    echo "❌ GHALA_APP_ID not set"
    echo "   Run: export GHALA_APP_ID='your_app_id'"
else
    echo "✅ GHALA_APP_ID is set"
fi

if [ -z "$GHALA_APP_SECRET" ]; then
    echo "❌ GHALA_APP_SECRET not set"
    echo "   Run: export GHALA_APP_SECRET='your_app_secret'"
else
    echo "✅ GHALA_APP_SECRET is set"
fi

echo ""
echo "🚀 Starting Ghala WhatsApp Bot..."
echo ""
echo "📋 Setup Checklist:"
echo "1. ✅ Sign up at https://dev.ghala.io/"
echo "2. ✅ Get your App ID and App Secret"
echo "3. ✅ Set environment variables (GHALA_APP_ID, GHALA_APP_SECRET)"
echo "4. ✅ Add webhook URL to Ghala dashboard:"
echo "   Webhook URL: https://your-domain.com/webhook"
echo "   Verify Token: tanzania_service_bot_verify_token"
echo ""
echo "🌐 For local testing:"
echo "   npm install -g ngrok"
echo "   ngrok http 5000"
echo "   Use ngrok URL as webhook URL"
echo ""
echo "🎯 Bot is ready for Tanzania WhatsApp users!"
echo "==================================================="

# Run the bot
python ghala_webhook_template.py
