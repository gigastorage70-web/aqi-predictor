# 📁 Project Structure - AQI Intelligence

## Clean, Organized File Structure

```
aqi-intelligence/
│
├── 📱 CORE APPLICATION FILES
│   ├── app.py                    # Main Streamlit web app
│   ├── predictor.py              # ML prediction engine
│   ├── train_model.py            # Model training script
│   ├── test_new_model.py         # Model testing script
│   └── aqi_model.pkl             # Trained ML model (0.81 MB)
│
├── 🛠️ UTILITIES (utils/)
│   ├── api.py                    # OpenWeatherMap API integration
│   ├── health.py                 # Health advisory engine
│   └── insights.py               # Smart insights generator
│
├── 📊 DATA (data/)
│   └── air_quality_health_monthly.csv  # Training dataset (6,600 records)
│
├── 📚 DOCUMENTATION (docs/)
│   ├── DEPLOYMENT.md             # Deployment guide (all platforms)
│   ├── TESTING.md                # Comprehensive testing guide
│   ├── MODEL_UPGRADE.md          # Model upgrade details
│   ├── PROJECT_SUMMARY.md        # Complete project overview
│   └── UPGRADE_COMPLETE.md       # Quick upgrade reference
│
├── ⚙️ CONFIGURATION (.streamlit/)
│   ├── config.toml               # Streamlit runtime settings
│   ├── secrets.toml              # API keys (not in git)
│   ├── secrets.toml.example      # API key template
│   └── manifest.json             # PWA manifest
│
├── 🚀 QUICK START
│   ├── quickstart.sh             # Linux/Mac quick start
│   └── quickstart.bat            # Windows quick start
│
├── 📋 PROJECT FILES
│   ├── README.md                 # Main documentation
│   ├── requirements.txt          # Python dependencies
│   ├── .gitignore               # Git ignore rules
│   └── PROJECT_STRUCTURE.md      # This file
│
└── 🗑️ ARCHIVED (unwanted_waste/)
    ├── app.py                    # Old app version
    ├── predictor.py              # Old predictor
    ├── model.py                  # Old model utilities
    ├── weather_api.py            # Old API module
    ├── train_and_save.py         # Old training script
    ├── data_aqi_cpcb.xml         # Old XML dataset
    ├── requirements.txt          # Old requirements
    └── aqi-prediction-model.ipynb # Original notebook
```

## 📂 Folder Descriptions

### Core Application Files (Root)
**Purpose**: Main application code that runs the AQI Intelligence app

- `app.py` - The main Streamlit web application with UI
- `predictor.py` - ML prediction engine with caching
- `train_model.py` - Script to retrain the model with new data
- `test_new_model.py` - Automated tests for model validation
- `aqi_model.pkl` - Pre-trained Gradient Boosting model

### Utils Folder
**Purpose**: Modular utility functions for clean code organization

- `api.py` - All OpenWeatherMap API calls with caching
- `health.py` - Health advisory generation based on AQI + weather
- `insights.py` - Smart insights and trend analysis

### Data Folder
**Purpose**: Training data and datasets

- `air_quality_health_monthly.csv` - 6,600 records from 2015-2024
  - Multiple Indian cities
  - Pollutant measurements
  - Weather conditions
  - Health metrics

### Docs Folder
**Purpose**: Comprehensive documentation

- `DEPLOYMENT.md` - Step-by-step deployment for Streamlit Cloud, Docker, Heroku, VPS
- `TESTING.md` - Complete testing checklist and procedures
- `MODEL_UPGRADE.md` - Details about the model upgrade
- `PROJECT_SUMMARY.md` - Full project overview and features
- `UPGRADE_COMPLETE.md` - Quick reference for the upgrade

### .streamlit Folder
**Purpose**: Streamlit configuration and secrets

- `config.toml` - Runtime settings (theme, server config)
- `secrets.toml` - API keys (gitignored for security)
- `secrets.toml.example` - Template for API key setup
- `manifest.json` - PWA configuration for mobile installation

### Unwanted Waste Folder
**Purpose**: Archive of old/deprecated files

Contains previous versions and deprecated code that's no longer needed but kept for reference.

## 🎯 File Usage Guide

### For Development

**Run the app:**
```bash
streamlit run app.py
```

**Test the model:**
```bash
python test_new_model.py
```

**Retrain the model:**
```bash
python train_model.py
```

### For Deployment

**Essential files to deploy:**
- `app.py`
- `predictor.py`
- `aqi_model.pkl`
- `utils/` (entire folder)
- `.streamlit/config.toml`
- `requirements.txt`

**Not needed for deployment:**
- `train_model.py` (only for retraining)
- `test_new_model.py` (only for testing)
- `data/` (only for training)
- `docs/` (only for documentation)
- `unwanted_waste/` (archived files)

### For Retraining

**Required files:**
- `train_model.py`
- `data/air_quality_health_monthly.csv`
- `requirements.txt`

**Output:**
- `aqi_model.pkl` (updated model)

## 📊 File Sizes

```
app.py                    ~15 KB
predictor.py              ~6 KB
train_model.py            ~8 KB
aqi_model.pkl             0.81 MB
utils/api.py              ~8 KB
utils/health.py           ~12 KB
utils/insights.py         ~6 KB
data/*.csv                ~1.2 MB
```

**Total project size**: ~2.5 MB (excluding docs and archived files)

## 🔄 File Dependencies

```
app.py
  ├── predictor.py
  │   └── aqi_model.pkl
  ├── utils/api.py
  ├── utils/health.py
  └── utils/insights.py

train_model.py
  ├── data/air_quality_health_monthly.csv
  └── aqi_model.pkl (output)

test_new_model.py
  └── predictor.py
```

## 🚫 What's in unwanted_waste/

**Old files that are no longer needed:**

1. `app.py` - Old version before production upgrade
2. `predictor.py` - Old predictor for XML-based model
3. `model.py` - Old model utilities (now in predictor.py)
4. `weather_api.py` - Old API module (now utils/api.py)
5. `train_and_save.py` - Old training script for XML data
6. `data_aqi_cpcb.xml` - Old XML dataset (454 records)
7. `requirements.txt` - Old dependencies
8. `aqi-prediction-model.ipynb` - Original Kaggle notebook

**Why keep them?**
- Reference for old implementation
- Rollback capability if needed
- Historical record of development

**Can be deleted?**
- Yes, if you're confident with the new version
- Recommended to keep for at least one release cycle

## 🎨 Clean Structure Benefits

### ✅ Easy Navigation
- Core files in root
- Utilities organized in folders
- Documentation separate
- Data isolated

### ✅ Clear Purpose
- Each file has a single responsibility
- Folder names are self-explanatory
- No clutter in root directory

### ✅ Deployment Ready
- Essential files clearly identified
- Easy to package for deployment
- Minimal file transfer needed

### ✅ Maintainable
- Easy to find and update files
- Modular structure
- Clear dependencies

### ✅ Professional
- Industry-standard structure
- Clean git repository
- Easy for collaborators

## 📝 Best Practices

### Adding New Files

**New utility module:**
```bash
# Add to utils/ folder
touch utils/new_module.py
```

**New documentation:**
```bash
# Add to docs/ folder
touch docs/NEW_GUIDE.md
```

**New data:**
```bash
# Add to data/ folder
cp new_dataset.csv data/
```

### Removing Files

**Don't delete immediately:**
```bash
# Move to unwanted_waste first
mv old_file.py unwanted_waste/
```

**After testing:**
```bash
# If everything works, then delete
rm -rf unwanted_waste/
```

## 🔍 Quick File Finder

**Need to...**

- Run the app? → `app.py`
- Make predictions? → `predictor.py`
- Retrain model? → `train_model.py`
- Test model? → `test_new_model.py`
- Deploy? → See `docs/DEPLOYMENT.md`
- Configure API? → `.streamlit/secrets.toml`
- Change theme? → `.streamlit/config.toml`
- Add health advice? → `utils/health.py`
- Modify API calls? → `utils/api.py`
- Update insights? → `utils/insights.py`

---

## ✅ Structure Verification

Run this to verify structure:
```bash
# Linux/Mac
tree -L 2 -I '__pycache__|*.pyc'

# Windows
tree /F /A
```

Expected output: Clean, organized structure as shown above.

---

**Last Updated**: After model upgrade and cleanup  
**Status**: ✅ Production-ready, clean, organized
