#!/bin/bash

# Setup script for AI Call Service

echo "=== AI Call Service Setup ==="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Warning: Some dependencies may have failed to install"
    echo "You may need to install system dependencies first"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env with your configuration"
fi

# Create recordings directory
echo ""
echo "Creating recordings directory..."
mkdir -p recordings

# Check for Ollama
echo ""
echo "Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo "Ollama is installed"
    echo "Pulling default model (llama2)..."
    ollama pull llama2
else
    echo "Warning: Ollama is not installed"
    echo "Install Ollama from: https://ollama.ai"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Ensure Ollama is running: ollama serve"
echo "3. Run the service: python main.py"
echo "   or as API: python api.py"
echo ""
echo "To activate the virtual environment later, run:"
echo "  source venv/bin/activate"
