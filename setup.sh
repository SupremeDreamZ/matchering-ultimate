#!/bin/bash

echo "🔥 MATCHERING ULTIMATE SUITE - SETUP SCRIPT 🔥"
echo "============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv matchering_env

# Activate virtual environment
echo "🔌 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source matchering_env/Scripts/activate
else
    # macOS/Linux
    source matchering_env/bin/activate
fi

# Install requirements
echo ""
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 TO START USING:"
echo "1. Activate the environment:"
echo "   source matchering_env/bin/activate"
echo ""
echo "2. Launch the Ultimate Control Center:"
echo "   python MATCHERING_ULTIMATE_CONTROL.py"
echo ""
echo "🔥 Enjoy the most powerful mastering system ever created!"
