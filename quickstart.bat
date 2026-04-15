@echo off
REM 🚀 AQI Intelligence - Quick Start Script (Windows)

echo 🌍 AQI Intelligence - Quick Start
echo ==================================
echo.

REM Check Python
echo 📋 Checking Python version...
python --version
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.12+
    pause
    exit /b 1
)
echo ✅ Python detected
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements_production.txt
echo ✅ Dependencies installed
echo.

REM Check for model
if not exist "aqi_model.pkl" (
    echo ⚠️  Model file not found!
    echo 📝 You need to train the model first:
    echo    python train_and_save.py --xml data_aqi_cpcb.xml
    echo.
    set /p has_data="Do you have the XML data file? (y/n): "
    
    if /i "%has_data%"=="y" (
        set /p xml_path="Enter path to XML file: "
        echo 🤖 Training model...
        python train_and_save.py --xml "%xml_path%"
        echo ✅ Model trained and saved
    ) else (
        echo ❌ Cannot proceed without model file
        echo 📥 Download from: https://www.kaggle.com/datasets/bhadramohit/india-air-quality-index2024-dataset
        pause
        exit /b 1
    )
) else (
    echo ✅ Model file found
)
echo.

REM Check for API key
if not exist ".streamlit\secrets.toml" (
    echo 🔑 API key not configured
    echo 📝 Creating secrets file...
    if not exist ".streamlit" mkdir .streamlit
    
    set /p api_key="Enter your OpenWeatherMap API key: "
    
    echo OPENWEATHER_API_KEY = "%api_key%" > .streamlit\secrets.toml
    
    echo ✅ API key saved
) else (
    echo ✅ API key configured
)
echo.

REM Run app
echo 🚀 Starting AQI Intelligence...
echo 📱 App will open in your browser
echo 🛑 Press Ctrl+C to stop
echo.

streamlit run app_production.py
