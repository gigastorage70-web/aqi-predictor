# 🌍 AQI Intelligence - Production Web App

A production-ready, mobile-first Air Quality Index (AQI) prediction and monitoring system built with Streamlit, Machine Learning, and real-time API integration.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create `.streamlit/secrets.toml`:
```toml
OPENWEATHER_API_KEY = "your_openweathermap_api_key"
```

Get a free API key at: https://openweathermap.org/api

### 3. Run App
```bash
streamlit run app.py
```

Or use the quick start scripts:
```bash
# Windows
quickstart.bat

# Linux/Mac
./quickstart.sh
```

## ✨ Features

- 🤖 **ML-Powered Predictions** - Gradient Boosting model (R²=0.9638)
- 📡 **Real-Time Data** - Live AQI, weather, and pollutants from OpenWeatherMap
- 🎯 **Dual AQI Display** - Compare ML predictions vs real-time measurements
- 💊 **Smart Health Advisory** - Context-aware recommendations
- 📈 **Historical Trends** - 7-day AQI visualization
- 🧪 **Pollutant Breakdown** - Detailed analysis of PM2.5, PM10, NO2, O3, CO
- 📍 **Location Intelligence** - Auto-detect or search by city
- 📱 **Mobile-First Design** - Responsive, PWA-installable

## 📁 Project Structure

```
aqi-intelligence/
│
├── app.py                    # Main Streamlit app
├── predictor.py              # ML prediction engine
├── train_model.py            # Model training script
├── test_new_model.py         # Model testing
├── aqi_model.pkl             # Trained model (0.81 MB)
│
├── utils/                    # Utility modules
│   ├── api.py               # API integration
│   ├── health.py            # Health advisory engine
│   └── insights.py          # Smart insights generator
│
├── data/                     # Data files
│   └── air_quality_health_monthly.csv
│
├── docs/                     # Documentation
│   ├── DEPLOYMENT.md        # Deployment guide
│   ├── TESTING.md           # Testing guide
│   ├── MODEL_UPGRADE.md     # Model details
│   └── PROJECT_SUMMARY.md   # Complete overview
│
├── .streamlit/              # Streamlit config
│   ├── config.toml          # Runtime settings
│   ├── secrets.toml         # API keys (not in git)
│   └── manifest.json        # PWA manifest
│
├── unwanted_waste/          # Old/deprecated files
│
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🎯 Model Performance

- **Training Data**: 6,600 records (2015-2024)
- **Test R²**: 0.9638 (96.38% accuracy)
- **Test RMSE**: 15.29 AQI points
- **Test MAE**: 11.94 AQI points
- **CV Score**: 0.9612 ± 0.0067

### Feature Importance
1. PM2.5: 84.4%
2. NO2: 7.0%
3. NH3: 2.1%
4. SO2: 1.5%
5. CO: 1.3%

## 💻 Usage

### Python API
```python
from predictor import predict_aqi

# Simple usage
result = predict_aqi({
    "pm25": 95.0,
    "pm10": 180.0,
    "no2": 45.0,
    "co": 1.2,
    "o3": 60.0
})

print(f"AQI: {result['aqi']}")
print(f"Category: {result['category']}")
print(f"Advice: {result['health_advice']}")
```

### Retrain Model
```bash
python train_model.py
```

### Test Model
```bash
python test_new_model.py
```

## 🌐 Deployment

### Streamlit Cloud (Recommended)

1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository
4. Add secrets:
```toml
OPENWEATHER_API_KEY = "your_key"
```
5. Deploy!

See `docs/DEPLOYMENT.md` for detailed instructions.

## 📊 API Integration

The app uses OpenWeatherMap API for:
- Current air pollution data
- Weather conditions
- Historical trends (7 days)
- Geocoding

**Free tier**: 1,000 calls/day (sufficient with caching)

## 🧪 Testing

```bash
# Run all tests
python test_new_model.py

# Test specific feature
python -c "from predictor import predict_aqi; print(predict_aqi({'pm25': 95}))"
```

See `docs/TESTING.md` for comprehensive testing guide.

## 📱 Mobile Installation

Users can install as PWA:
1. Open app in mobile browser
2. Tap "Share" → "Add to Home Screen"
3. App icon appears on home screen

## 🔧 Configuration

### `.streamlit/config.toml`
```toml
[server]
headless = true
enableCORS = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
```

### Environment Variables
```bash
export OPENWEATHER_API_KEY="your_key"
```

## 📚 Documentation

- **Deployment Guide**: `docs/DEPLOYMENT.md`
- **Testing Guide**: `docs/TESTING.md`
- **Model Details**: `docs/MODEL_UPGRADE.md`
- **Project Overview**: `docs/PROJECT_SUMMARY.md`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 📄 License

MIT License - free for personal and commercial use

## 🙏 Acknowledgments

- OpenWeatherMap for API access
- Kaggle for AQI dataset
- Streamlit for the framework

## 📞 Support

- **Documentation**: Check `docs/` folder
- **Issues**: GitHub Issues
- **Testing**: Run `test_new_model.py`

---

**Built with ❤️ using Python, Streamlit, and Machine Learning**

🚀 **Ready for production deployment!**
