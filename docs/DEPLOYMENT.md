# 🚀 Deployment Guide - AQI Intelligence

## Pre-Deployment Checklist

- [ ] Model file `aqi_model.pkl` exists (run `train_and_save.py` if not)
- [ ] OpenWeatherMap API key obtained
- [ ] All dependencies in `requirements_production.txt`
- [ ] Code tested locally with `streamlit run app_production.py`

## Option 1: Streamlit Cloud (Recommended)

### Step 1: Prepare GitHub Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Production-ready AQI Intelligence app"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/aqi-intelligence.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repository
4. Set:
   - **Branch**: `main`
   - **Main file path**: `app_production.py`
   - **Python version**: 3.12
5. Click "Advanced settings" → "Secrets"
6. Add:
```toml
OPENWEATHER_API_KEY = "your_actual_api_key_here"
```
7. Click "Deploy"

### Step 3: Wait for Deployment

- Initial deployment takes 2-5 minutes
- App will be live at: `https://your-app-name.streamlit.app`

### Step 4: Test

- Open app URL
- Try city search
- Try "My Location" button
- Verify all features work

## Option 2: Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements_production.txt .
RUN pip install --no-cache-dir -r requirements_production.txt

# Copy app files
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
CMD ["streamlit", "run", "app_production.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build and Run

```bash
# Build image
docker build -t aqi-intelligence .

# Run container
docker run -p 8501:8501 \
  -e OPENWEATHER_API_KEY="your_key" \
  aqi-intelligence
```

### Deploy to Cloud

**AWS ECS / Google Cloud Run / Azure Container Instances**

1. Push image to container registry
2. Create service with environment variable `OPENWEATHER_API_KEY`
3. Expose port 8501
4. Set health check endpoint: `/_stcore/health`

## Option 3: Heroku

### Create `Procfile`

```
web: streamlit run app_production.py --server.port=$PORT --server.address=0.0.0.0
```

### Deploy

```bash
# Login to Heroku
heroku login

# Create app
heroku create aqi-intelligence

# Set API key
heroku config:set OPENWEATHER_API_KEY="your_key"

# Deploy
git push heroku main

# Open app
heroku open
```

## Option 4: VPS (DigitalOcean, Linode, etc.)

### Setup Script

```bash
#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.12 python3-pip -y

# Clone repo
git clone https://github.com/YOUR_USERNAME/aqi-intelligence.git
cd aqi-intelligence

# Install dependencies
pip3 install -r requirements_production.txt

# Set API key
export OPENWEATHER_API_KEY="your_key"

# Run with nohup
nohup streamlit run app_production.py --server.port=8501 &
```

### Setup Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## Post-Deployment

### 1. Monitor Performance

- Check Streamlit Cloud metrics
- Monitor API usage on OpenWeatherMap dashboard
- Set up uptime monitoring (UptimeRobot, Pingdom)

### 2. Enable HTTPS

- Streamlit Cloud: Automatic
- Custom domain: Use Let's Encrypt / Cloudflare

### 3. Custom Domain (Optional)

**Streamlit Cloud:**
1. Go to app settings
2. Add custom domain
3. Update DNS records

### 4. Analytics (Optional)

Add to `app_production.py`:

```python
# Google Analytics
st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""", unsafe_allow_html=True)
```

## Troubleshooting

### App won't start

- Check logs in Streamlit Cloud dashboard
- Verify `aqi_model.pkl` is in repository
- Ensure API key is set correctly

### API errors

- Verify API key is active
- Check OpenWeatherMap account status
- Ensure API calls are within free tier limits

### Slow performance

- Check cache settings in `utils/api.py`
- Verify model is cached with `@st.cache_resource`
- Consider upgrading Streamlit Cloud plan

### Mobile issues

- Test on actual devices
- Check responsive CSS in `app_production.py`
- Verify PWA manifest is accessible

## Maintenance

### Update Dependencies

```bash
pip list --outdated
pip install --upgrade streamlit pandas numpy
pip freeze > requirements_production.txt
```

### Retrain Model

```bash
# Get latest data
python train_and_save.py --xml new_data.xml

# Test locally
streamlit run app_production.py

# Commit and push
git add aqi_model.pkl
git commit -m "Update model with latest data"
git push
```

### Monitor API Usage

- OpenWeatherMap free tier: 1,000 calls/day
- With caching (5-10 min TTL): ~100-200 users/day
- Upgrade to paid plan if needed

## Success Metrics

- ✅ App loads in < 3 seconds
- ✅ API calls cached properly
- ✅ Mobile responsive on all devices
- ✅ No errors in logs
- ✅ Health advisory displays correctly
- ✅ Charts render smoothly

## Support

- Streamlit Docs: https://docs.streamlit.io
- Community Forum: https://discuss.streamlit.io
- GitHub Issues: Your repo issues page

---

🎉 Your AQI Intelligence app is now live!
