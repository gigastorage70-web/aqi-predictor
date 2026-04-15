"""
🌍 AQI Intelligence - Production Web App
Mobile-first, scalable, production-ready AQI prediction system
"""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval

# Import custom modules
from predictor import predict_aqi
from utils.api import (
    fetch_city_coordinates,
    fetch_current_pollution,
    fetch_current_weather,
    fetch_historical_pollution,
    reverse_geocode,
    get_api_key,
    owm_aqi_to_us_aqi,
    APIError,
    CityNotFoundError
)
from utils.health import (
    get_aqi_category,
    generate_health_advice,
    get_pollutant_info
)
from utils.insights import (
    generate_comparison_insight,
    generate_trend_insights,
    generate_weather_impact_insight,
    generate_daily_summary,
    get_pollutant_breakdown,
    generate_notification_message
)

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="AQI Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "AQI Intelligence - Real-time air quality monitoring with ML predictions"
    }
)

# PWA Meta Tags for Mobile Installation
st.markdown("""
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#667eea">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="AQI Intel">
    <link rel="manifest" href=".streamlit/manifest.json">
    <link rel="apple-touch-icon" href="/icon-192.png">
</head>
""", unsafe_allow_html=True)

# ============================================================================
# CUSTOM CSS - Mobile-First Design
# ============================================================================

st.markdown("""
<style>
    /* Mobile-first responsive design */
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 16px;
        margin-bottom: 1.5rem;
    }
    
    .aqi-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .aqi-number {
        font-size: 4rem;
        font-weight: 900;
        line-height: 1;
        margin: 0.5rem 0;
    }
    
    .aqi-label {
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .weather-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 20px;
        padding: 1.5rem;
        color: white;
        margin: 0.5rem 0;
    }
    
    .insight-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .health-advice {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .comparison-panel {
        background: #fff;
        border: 2px solid #e0e0e0;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .pollutant-bar {
        background: #e0e0e0;
        border-radius: 10px;
        height: 24px;
        margin: 0.5rem 0;
        overflow: hidden;
    }
    
    .pollutant-fill {
        height: 100%;
        border-radius: 10px;
        display: flex;
        align-items: center;
        padding: 0 0.5rem;
        font-size: 0.85rem;
        font-weight: 600;
        color: white;
    }
    
    /* Mobile optimization */
    @media (max-width: 768px) {
        .aqi-number { font-size: 3rem; }
        .main-header h1 { font-size: 1.5rem; }
    }
    
    /* PWA-ready styles */
    .install-prompt {
        background: #4CAF50;
        color: white;
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "city" not in st.session_state:
    st.session_state.city = ""
if "lat" not in st.session_state:
    st.session_state.lat = None
if "lon" not in st.session_state:
    st.session_state.lon = None
if "pollution_data" not in st.session_state:
    st.session_state.pollution_data = None
if "weather_data" not in st.session_state:
    st.session_state.weather_data = None
if "predicted_aqi" not in st.session_state:
    st.session_state.predicted_aqi = None
if "geo_pending" not in st.session_state:
    st.session_state.geo_pending = False
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>🌍 AQI Intelligence</h1>
    <p style="margin:0; opacity:0.9;">Real-time Air Quality Monitoring & ML Predictions</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# API KEY CHECK
# ============================================================================

api_key = get_api_key()

if not api_key:
    st.warning("⚠️ OpenWeatherMap API key not configured. Add it to Streamlit secrets or environment variables.")
    with st.expander("🔑 How to add API key"):
        st.code("""
# In .streamlit/secrets.toml:
OPENWEATHER_API_KEY = "your_key_here"

# Or set environment variable:
export OPENWEATHER_API_KEY="your_key_here"
        """)
    st.stop()

# ============================================================================
# LOCATION INPUT SECTION
# ============================================================================

st.markdown("### 📍 Select Location")

col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    city_input = st.text_input(
        "City Name",
        placeholder="e.g., Delhi, London, New York",
        label_visibility="collapsed"
    )

with col2:
    fetch_btn = st.button("🌐 Fetch", use_container_width=True, type="primary")

with col3:
    location_btn = st.button("📍 My Location", use_container_width=True)

# Handle geolocation
if location_btn:
    st.session_state.geo_pending = True

if st.session_state.geo_pending:
    coords = streamlit_js_eval(
        js_expressions="""
            new Promise((resolve) => {
                if (!navigator.geolocation) { resolve(null); return; }
                navigator.geolocation.getCurrentPosition(
                    p => resolve({lat: p.coords.latitude, lon: p.coords.longitude}),
                    () => resolve(null),
                    {timeout: 10000}
                );
            })
        """,
        key="geo_detect"
    )
    
    if coords is None:
        st.info("📡 Waiting for location permission...")
    elif coords in ("null", False):
        st.error("❌ Location access denied")
        st.session_state.geo_pending = False
    else:
        try:
            lat, lon = float(coords["lat"]), float(coords["lon"])
            st.session_state.lat = lat
            st.session_state.lon = lon
            st.session_state.city = reverse_geocode(lat, lon, api_key)
            st.session_state.geo_pending = False
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.session_state.geo_pending = False

# Handle city fetch
if fetch_btn and city_input:
    with st.spinner(f"🔍 Fetching data for {city_input}..."):
        try:
            lat, lon, resolved_city = fetch_city_coordinates(city_input, api_key)
            st.session_state.lat = lat
            st.session_state.lon = lon
            st.session_state.city = resolved_city
            st.success(f"✅ Location set: {resolved_city}")
            st.rerun()
        except CityNotFoundError as e:
            st.error(f"🔍 {e}")
        except APIError as e:
            st.error(f"🌐 {e}")
        except Exception as e:
            st.error(f"❌ {e}")

# ============================================================================
# MAIN APP LOGIC - Only if location is set
# ============================================================================

if st.session_state.lat and st.session_state.lon:
    
    lat = st.session_state.lat
    lon = st.session_state.lon
    city = st.session_state.city
    
    # Fetch all data
    with st.spinner("📊 Loading real-time data..."):
        try:
            pollution = fetch_current_pollution(lat, lon, api_key)
            weather = fetch_current_weather(lat, lon, api_key)
            st.session_state.pollution_data = pollution
            st.session_state.weather_data = weather
        except Exception as e:
            st.error(f"❌ Failed to fetch data: {e}")
            st.stop()
    
    # Generate ML prediction
    with st.spinner("🤖 Running ML prediction..."):
        try:
            pred_input = {
                "pm25": pollution["pm25"],
                "pm10": pollution["pm10"],
                "no2": pollution["no2"],
                "co": pollution["co"],
                "o3": pollution["o3"]
            }
            result = predict_aqi(pred_input)
            predicted_aqi = result["aqi"]
            st.session_state.predicted_aqi = predicted_aqi
        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")
            predicted_aqi = None
    
    # ========================================================================
    # DISPLAY SECTION
    # ========================================================================
    
    st.markdown(f"## 📍 {city}")
    st.caption(f"📅 {datetime.now().strftime('%A, %B %d, %Y • %I:%M %p')}")
    
    # Daily summary
    if predicted_aqi and weather:
        category_info = get_aqi_category(predicted_aqi)
        summary = generate_daily_summary(predicted_aqi, category_info["category"], weather)
        st.info(summary)
    
    # Notification message
    if predicted_aqi:
        notif = generate_notification_message(predicted_aqi)
        if notif:
            st.warning(notif)
    
    st.divider()
    
    # ========================================================================
    # DUAL AQI DISPLAY
    # ========================================================================
    
    st.markdown("### 🎯 AQI Comparison")
    
    col_pred, col_real = st.columns(2)
    
    # ML Prediction
    with col_pred:
        if predicted_aqi:
            cat = get_aqi_category(predicted_aqi)
            st.markdown(f"""
            <div class="aqi-card" style="background:{cat['color']};color:{cat['text_color']};">
                <div style="font-size:0.9rem;opacity:0.8;">🤖 ML PREDICTION</div>
                <div class="aqi-number">{predicted_aqi:.0f}</div>
                <div class="aqi-label">{cat['emoji']} {cat['category']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Real-time AQI
    with col_real:
        if pollution:
            real_aqi = owm_aqi_to_us_aqi(pollution["aqi_index"])
            cat = get_aqi_category(real_aqi)
            st.markdown(f"""
            <div class="aqi-card" style="background:{cat['color']};color:{cat['text_color']};">
                <div style="font-size:0.9rem;opacity:0.8;">📡 REAL-TIME</div>
                <div class="aqi-number">{real_aqi:.0f}</div>
                <div class="aqi-label">{cat['emoji']} {cat['category']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Comparison insight
    if predicted_aqi and pollution:
        real_aqi = owm_aqi_to_us_aqi(pollution["aqi_index"])
        insight = generate_comparison_insight(predicted_aqi, real_aqi)
        
        st.markdown(f"""
        <div class="comparison-panel">
            <h4 style="margin-top:0;">{insight['emoji']} Model Accuracy: {insight['accuracy'].title()}</h4>
            <p style="font-size:1.1rem;margin:0.5rem 0;">{insight['message']}</p>
            <div style="display:flex;gap:1rem;margin-top:1rem;">
                <div class="metric-card" style="flex:1;">
                    <div style="font-size:0.8rem;color:#666;">Difference</div>
                    <div style="font-size:1.8rem;font-weight:800;color:{insight['color']};">
                        {insight['difference']:.1f}
                    </div>
                </div>
                <div class="metric-card" style="flex:1;">
                    <div style="font-size:0.8rem;color:#666;">Error %</div>
                    <div style="font-size:1.8rem;font-weight:800;color:{insight['color']};">
                        {insight['percentage']:.1f}%
                    </div>
                </div>
            </div>
            <p style="font-size:0.9rem;color:#666;margin-top:1rem;">💡 {insight['reason']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # ========================================================================
    # WEATHER CONDITIONS
    # ========================================================================
    
    st.markdown("### 🌤️ Current Weather")
    
    if weather:
        icon_url = f"https://openweathermap.org/img/wn/{weather['icon']}@4x.png"
        
        col_w1, col_w2 = st.columns([1, 2])
        
        with col_w1:
            st.image(icon_url, width=150)
        
        with col_w2:
            st.markdown(f"""
            <div style="padding:1rem 0;">
                <div style="font-size:3rem;font-weight:800;">{weather['temp_c']}°C</div>
                <div style="font-size:1.2rem;margin:0.5rem 0;">{weather['description']}</div>
                <div style="font-size:0.9rem;color:#666;">Feels like {weather['feels_like']}°C</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Weather metrics
        w_cols = st.columns(4)
        w_cols[0].metric("💧 Humidity", f"{weather['humidity']}%")
        w_cols[1].metric("💨 Wind", f"{weather['wind_speed']} km/h")
        w_cols[2].metric("👁️ Visibility", f"{weather['visibility']//1000} km")
        w_cols[3].metric("🌡️ Pressure", f"{weather['pressure']} hPa")
        
        # Weather impact insight
        if predicted_aqi:
            impact = generate_weather_impact_insight(
                predicted_aqi, weather['temp_c'], weather['humidity']
            )
            if impact:
                st.info(f"🌡️ {impact}")
    
    st.divider()
    
    # ========================================================================
    # HEALTH ADVISORY
    # ========================================================================
    
    st.markdown("### 💊 Health Advisory")
    
    if predicted_aqi and weather:
        advice = generate_health_advice(
            predicted_aqi,
            weather['temp_c'],
            weather['humidity']
        )
        
        st.markdown(f"""
        <div class="health-advice">
            <h4 style="margin-top:0;">📋 General Advice</h4>
            <p style="font-size:1.1rem;">{advice['general_advice']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Precautions
        if advice['precautions']:
            st.markdown("#### ⚠️ Precautions")
            for prec in advice['precautions']:
                st.markdown(f"- {prec}")
        
        # Risk groups
        if advice['risk_groups']:
            st.markdown("#### 👥 At-Risk Groups")
            for group in advice['risk_groups']:
                st.markdown(f"- {group}")
        
        # Activities
        if advice['activities']:
            st.markdown("#### 🏃 Activity Recommendations")
            act_cols = st.columns(len(advice['activities']))
            for idx, (activity, status) in enumerate(advice['activities'].items()):
                with act_cols[idx]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="font-size:0.8rem;color:#666;">{activity.replace('_', ' ').title()}</div>
                        <div style="font-size:1.1rem;margin-top:0.5rem;">{status}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    st.divider()
    
    # ========================================================================
    # POLLUTANT BREAKDOWN
    # ========================================================================
    
    st.markdown("### 🧪 Pollutant Analysis")
    
    if pollution:
        pollutants = {
            "PM2.5": pollution["pm25"],
            "PM10": pollution["pm10"],
            "NO2": pollution["no2"],
            "O3": pollution["o3"],
            "CO": pollution["co"] * 1000  # Convert back for display
        }
        
        breakdown = get_pollutant_breakdown(pollutants)
        
        for item in breakdown:
            info = get_pollutant_info(item["name"], item["value"])
            if info:
                st.markdown(f"""
                <div style="margin:1rem 0;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
                        <span><strong>{item['emoji']} {info['name']}</strong></span>
                        <span>{info['status']}</span>
                    </div>
                    <div class="pollutant-bar">
                        <div class="pollutant-fill" style="width:{min(item['percentage'], 100)}%;
                             background:linear-gradient(90deg, #667eea 0%, #764ba2 100%);">
                            {item['value']:.1f} {info['unit']} ({item['percentage']}%)
                        </div>
                    </div>
                    <div style="font-size:0.85rem;color:#666;margin-top:0.25rem;">
                        {info['health_impact']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.divider()
    
    # ========================================================================
    # HISTORICAL TRENDS
    # ========================================================================
    
    st.markdown("### 📈 7-Day AQI Trend")
    
    try:
        with st.spinner("Loading historical data..."):
            history = fetch_historical_pollution(lat, lon, 7, api_key)
            
            if history:
                # Generate predictions for historical data
                hist_df = []
                for day in history:
                    try:
                        day_pred = predict_aqi({
                            "pm25": day["pm25"],
                            "pm10": day["pm10"],
                            "no2": day["no2"],
                            "co": day["co"],
                            "o3": day["o3"]
                        })
                        hist_df.append({
                            "Date": pd.to_datetime(day["date"]),
                            "Predicted AQI": day_pred["aqi"],
                            "Real AQI": owm_aqi_to_us_aqi(int(day["aqi_index"]))
                        })
                    except:
                        continue
                
                if hist_df:
                    df = pd.DataFrame(hist_df)
                    
                    # Melt for Altair
                    df_melt = df.melt("Date", var_name="Type", value_name="AQI")
                    
                    # Create chart
                    chart = alt.Chart(df_melt).mark_line(point=True, strokeWidth=3).encode(
                        x=alt.X("Date:T", title="Date", axis=alt.Axis(format="%b %d")),
                        y=alt.Y("AQI:Q", title="AQI", scale=alt.Scale(domain=[0, 300])),
                        color=alt.Color("Type:N", scale=alt.Scale(
                            domain=["Predicted AQI", "Real AQI"],
                            range=["#667eea", "#f5576c"]
                        )),
                        tooltip=["Date:T", "Type:N", alt.Tooltip("AQI:Q", format=".1f")]
                    ).properties(height=300)
                    
                    st.altair_chart(chart, use_container_width=True)
                    
                    # Trend insights
                    insights = generate_trend_insights(history)
                    if insights:
                        st.markdown("#### 💡 Trend Insights")
                        for insight in insights:
                            st.info(insight)
    
    except Exception as e:
        st.warning(f"Historical data unavailable: {e}")
    
    st.divider()
    
    # ========================================================================
    # FOOTER
    # ========================================================================
    
    st.markdown("""
    <div style="text-align:center;padding:2rem 0;color:#666;">
        <p>🌍 AQI Intelligence • Powered by ML & OpenWeatherMap</p>
        <p style="font-size:0.85rem;">Data updates every 5 minutes • Predictions cached for performance</p>
    </div>
    """, unsafe_allow_html=True)

else:
    # No location set - show welcome screen
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;">
        <h2>👋 Welcome to AQI Intelligence</h2>
        <p style="font-size:1.1rem;color:#666;margin:1rem 0;">
            Get real-time air quality data and ML-powered predictions for any location worldwide.
        </p>
        <p style="margin-top:2rem;">
            👆 Enter a city name or use your location to get started
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    cols = st.columns(3)
    with cols[0]:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:2rem;">🤖</div>
            <h4>ML Predictions</h4>
            <p style="font-size:0.9rem;color:#666;">Advanced machine learning model trained on real data</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:2rem;">📡</div>
            <h4>Real-Time Data</h4>
            <p style="font-size:0.9rem;color:#666;">Live AQI and weather from OpenWeatherMap</p>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size:2rem;">💊</div>
            <h4>Health Advice</h4>
            <p style="font-size:0.9rem;color:#666;">Personalized recommendations based on conditions</p>
        </div>
        """, unsafe_allow_html=True)
