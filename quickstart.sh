#!/bin/bash

# 🚀 AQI Intelligence - Quick Start Script

echo "🌍 AQI Intelligence - Quick Start"
echo "=================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version detected"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements_production.txt
echo "✅ Dependencies installed"
echo ""

# Check for model file
if [ ! -f "aqi_model.pkl" ]; then
    echo "⚠️  Model file not found!"
    echo "📝 You need to train the model first:"
    echo "   python train_and_save.py --xml data_aqi_cpcb.xml"
    echo ""
    read -p "Do you have the XML data file? (y/n): " has_data
    
    if [ "$has_data" = "y" ]; then
        read -p "Enter path to XML file: " xml_path
        echo "🤖 Training model..."
        python3 train_and_save.py --xml "$xml_path"
        echo "✅ Model trained and saved"
    else
        echo "❌ Cannot proceed without model file"
        echo "📥 Download data from: https://www.kaggle.com/datasets/bhadramohit/india-air-quality-index2024-dataset"
        exit 1
    fi
else
    echo "✅ Model file found"
fi
echo ""

# Check for API key
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "🔑 API key not configured"
    echo "📝 Creating secrets file..."
    mkdir -p .streamlit
    
    read -p "Enter your OpenWeatherMap API key: " api_key
    
    cat > .streamlit/secrets.toml << EOF
OPENWEATHER_API_KEY = "$api_key"
EOF
    
    echo "✅ API key saved to .streamlit/secrets.toml"
else
    echo "✅ API key configured"
fi
echo ""

# Run app
echo "🚀 Starting AQI Intelligence..."
echo "📱 App will open in your browser"
echo "🛑 Press Ctrl+C to stop"
echo ""

streamlit run app_production.py
