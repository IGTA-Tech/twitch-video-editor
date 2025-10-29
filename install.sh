#!/bin/bash
# Installation script for StreamCut Pro (Mac/Linux)

echo "================================================"
echo "  StreamCut Pro - Installation Script"
echo "================================================"
echo ""

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $PYTHON_VERSION"
echo ""

# Check FFmpeg
echo "Checking FFmpeg installation..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg is not installed."
    echo ""
    echo "Please install FFmpeg:"
    echo "  Mac: brew install ffmpeg"
    echo "  Linux: sudo apt install ffmpeg"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1)
    echo "✓ Found $FFMPEG_VERSION"
fi
echo ""

# Install Python dependencies
echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Error installing dependencies"
    exit 1
fi
echo ""

# Make main.py executable
chmod +x main.py

echo "================================================"
echo "  Installation Complete!"
echo "================================================"
echo ""
echo "To run StreamCut Pro:"
echo "  ./main.py"
echo ""
echo "Or:"
echo "  python3 main.py"
echo ""
echo "For more information, see README.md"
echo ""
