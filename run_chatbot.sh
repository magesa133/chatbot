#!/bin/bash
# Quick start script for Tanzania Service Chatbot

echo "🇹🇿 Starting Tanzania Location-Based Service Chatbot..."
echo "=================================================="

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

# Activate virtual environment and run chatbot
echo "🔧 Activating virtual environment..."
source ../../tanzania_chatbot_env/bin/activate

echo "🚀 Starting chatbot with OpenStreetMap integration..."
echo "Type 'quit' to exit"
echo ""

python main.py

echo ""
echo "👋 Chatbot stopped. Thanks for using Tanzania Service Finder!"
