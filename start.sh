#!/bin/bash

# Clash of Clans Discord Bot Web Portal Startup Script

echo "🛡️ Starting COC Discord Bot Web Portal..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r website_requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ Warning: .env file not found!"
    echo "Please create a .env file with your API_TOKEN:"
    echo "API_TOKEN=your_clash_of_clans_api_token_here"
    echo ""
    echo "You can get an API token from: https://developer.clashofclans.com/"
    exit 1
fi

# Set Flask environment
export FLASK_ENV=development
export FLASK_DEBUG=True

echo "🚀 Starting the web application..."
echo "📱 Open your browser and go to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Run the Flask application
python app.py