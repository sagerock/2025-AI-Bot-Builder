#!/bin/bash

# AI Bot Builder - Quick Start Script

set -e

echo "🤖 AI Bot Builder - Quick Start"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your settings!"
    echo "   At minimum, set:"
    echo "   - SECRET_KEY (use a random string)"
    echo "   - ADMIN_PASSWORD"
    echo ""
    read -p "Press Enter when you've edited .env file..."
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create data directory
mkdir -p data

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting server..."
echo "   Admin Dashboard: http://localhost:8000/admin"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
