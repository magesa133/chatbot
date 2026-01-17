#!/bin/bash
# WhatsApp Mode Runner for Tanzania Service Chatbot

echo "🇹🇿 Tanzania Service Chatbot - WhatsApp Mode"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the chatbot directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "../../tanzania_chatbot_env" ]; then
    echo "❌ Error: Virtual environment not found. Please run:"
    echo "   python3 -m venv tanzania_chatbot_env"
    echo "   source tanzania_chatbot_env/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../../tanzania_chatbot_env/bin/activate

# Install any missing dependencies
echo "📦 Ensuring dependencies are installed..."
pip install -q flask python-dotenv

# Check if Meta WhatsApp credentials are configured
if [ -z "$WHATSAPP_ACCESS_TOKEN" ] || [ -z "$WHATSAPP_PHONE_NUMBER_ID" ]; then
    echo ""
    echo "⚠️  Warning: Meta WhatsApp credentials not found!"
    echo ""
    echo "To set up WhatsApp integration:"
    echo "1. 📝 Set up Meta WhatsApp Business API:"
    echo "   - Go to developers.facebook.com"
    echo "   - Create WhatsApp Business API app"
    echo "2. 🌐 Set environment variables:"
    echo ""
    echo "   export WHATSAPP_ACCESS_TOKEN='your_access_token'"
    echo "   export WHATSAPP_PHONE_NUMBER_ID='your_phone_number_id'"
    echo "   export WHATSAPP_WABA_ID='your_waba_id'"
    echo "   export WHATSAPP_WEBHOOK_TOKEN='your_webhook_token'"
    echo ""
    echo "For local testing, you can use ngrok:"
    echo "   npm install -g ngrok  # Install ngrok"
    echo "   ngrok http 5000       # Expose local server"
    echo ""
    echo "Starting server anyway (will show setup instructions)..."
    echo ""
fi

echo "🚀 Starting WhatsApp chatbot server..."
echo "📱 Webhook URL will be shown below"
echo "❤️  Health check: http://localhost:5000/health"
echo "🇹🇿 Ready for Tanzania WhatsApp users!"
echo "=============================================="

# Run the WhatsApp server
python main.py --whatsapp
