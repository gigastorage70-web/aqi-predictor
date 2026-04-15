"""
app.py  –  Smart AQI Predictor  🌍
Run with:  streamlit run app.py
"""

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

from predictor import predict_aqi
from weather_api import (
    fetch_pollution_by_city,
    fetch_pollution_by_coords,
    fetch_historical_pollution,
    fetch_current_weather,
    fetch_official_aqi,
    APIKeyMissingError,
    CityNotFoundError,
    APIError,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Smart AQI Predictor",
    page_icon="🌍",
    layout="wide",
)

# ---------------------------------------------------------------------------
# AQI colour palette
# ---------------------------------------------------------------------------
CATEGORY_STYLE = {
    "Good":                           {"bg": "#00e400", "fg": "#000000", "emoji": "😊"},
    "Moderate":                       {"bg": "#ffff00", "fg": "#000000", "emoji": "😐"},
    "Unhealthy for Sensitive Groups": {"bg": "#ff7e00", "fg": "#000000", "emoji": "😷"},
    "Unhealthy":                      {"bg": "#ff0000", "fg": "#ffffff", "emoji": "🤢"},
    "Very Unhealthy":                 {"bg": "#8f3f97", "fg": "#ffffff", "emoji": "🚨"},
    "Hazardous":                      {"bg": "#7e0023", "fg": "#ffffff", "emoji": "☠️"},
}

OWM_AQI_STYLE = {
    1: {"bg": "#00e400", "fg": "#000000", "label": "Good"},
    2: {"bg": "#a8e05f", "fg": "#000000", "label": "Fair"},
    3: {"bg": "#ffff00", "fg": "#000000", "label": "Moderate"},
    4: {"bg": "#ff7e00", "fg": "#000000", "label": "Poor"},
    5: {"bg": "#ff0000", "fg": "#ffffff", "label": "Very Poor"},
}

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .aqi-card {
        border-radius: 16px; padding: 24px 28px;
        text-align: center; margin: 8px 0;
    }
    .aqi-number  { font-size: 64px; font-weight: 800; line-height: 1; }
    .aqi-label   { font-size: 18px; font-weight: 600; margin-top: 6px; }
    .advice-box  {
        background: #f0f4ff; border-left: 5px solid #4a6cf7;
        border-radius: 8px; padding: 12px 16px;
        font-size: 14px; color: #1a1a2e; margin-top: 10px;
    }
    .weather-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px; padding: 20px 24px; color: #fff; margin: 8px 0;
    }
    .weather-temp { font-size: 48px; font-weight: 800; line-height: 1; }
    .weather-desc { font-size: 15px; opacity: 0.8; margin-top: 4px; }
    .compare-box  {
        border-radius: 12px; padding: 16px 20px; margin: 6px 0;
        border: 1px solid #e0e0e0;
    }
    .source-badge {
        display: inline-block; font-size: 11px; font-weight: 600;
        padding: 2px 10px; border-radius: 20px; margin-bottom: 8px;
    }
    .metric-row { display: flex; gap: 12px; flex-wrap: wrap; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dummy_trend(anchor_aqi: float | None = None) -> pd.DataFrame:
    rng        = np.random.default_rng(seed=42)
    base       = anchor_aqi if anchor_aqi else 120.0
    noise      = rng.integers(-25, 25, size=7).astype(float)
    aqi_values = np.clip(base + noise, 10, 400)
    dates      = pd.date_range(end=pd.Timestamp.today().normalize(), periods=7, freq="D")
    return pd.DataFrame({"Date": dates, "AQI": aqi_values.round(1)})


def _owm_to_us_aqi(owm_index: int) -> float:
    """Map OWM 1-5 index to approximate US AQI midpoint for comparison."""
    return {1: 25.0, 2: 75.0, 3: 125.0, 4: 175.0, 5: 275.0}.get(owm_index, 0.0)


def _accuracy_color(pct_error: float) -> str:
    if pct_error <= 10:  return "#00c853"
    if pct_error <= 20:  return "#ffd600"
    if pct_error <= 35:  return "#ff6d00"
    return "#d50000"


def _trend_chart(trend_df: pd.DataFrame, predicted_aqi: float | None = None) -> alt.Chart:
    thresholds = [
        {"y": 0,   "y2": 50,  "color": "#00e40033"},
        {"y": 50,  "y2": 100, "color": "#ffff0033"},
        {"y": 100, "y2": 150, "color": "#ff7e0033"},
        {"y": 150, "y2": 200, "color": "#ff000033"},
        {"y": 200, "y2": 300, "color": "#8f3f9733"},
        {"y": 300, "y2": 420, "color": "#7e002333"},
    ]
    bands = alt.Chart(pd.DataFrame(thresholds)).mark_rect(opacity=0.35).encode(
        y=alt.Y("y:Q"), y2=alt.Y2("y2:Q"),
        color=alt.Color("color:N", scale=None, legend=None),
    )

    y_max = max(420, int(trend_df["AQI"].max()) + 30)

    line = (
        alt.Chart(trend_df)
        .mark_line(point=True, strokeWidth=2.5, color="#4a6cf7")
        .encode(
            x=alt.X("Date:T", title="Date",
                    axis=alt.Axis(format="%b %d", labelAngle=-30)),
            y=alt.Y("AQI:Q", title="AQI",
                    scale=alt.Scale(domain=[0, y_max])),
            tooltip=[
                alt.Tooltip("Date:T", format="%A, %b %d"),
                alt.Tooltip("AQI:Q", format=".1f"),
            ],
        )
    )
    labels = line.mark_text(dy=-12, fontSize=11, color="#1a1a2e").encode(
        text=alt.Text("AQI:Q", format=".0f")
    )

    layers = [bands, line, labels]

    # Overlay today's prediction as a dashed rule
    if predicted_aqi is not None:
        rule_df = pd.DataFrame([{"y": predicted_aqi}])
        rule = (
            alt.Chart(rule_df)
            .mark_rule(strokeDash=[6, 3], color="#ff6d00", strokeWidth=1.5)
            .encode(y=alt.Y("y:Q"))
        )
        layers.append(rule)

    return alt.layer(*layers).properties(height=280).configure_view(strokeWidth=0)


# ---------------------------------------------------------------------------
# Session-state defaults
# ---------------------------------------------------------------------------
_DEFAULTS = dict(
    pm25=None, pm10=None, no2=None, co=None, o3=None,
    fetched_city="", data_source="manual",
    geo_lat=None, geo_lon=None, geo_pending=False,
    live_weather=None, live_aqi_data=None,
)
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    try:
        _secret_key = st.secrets.get("OPENWEATHER_API_KEY", "")
    except Exception:
        _secret_key = ""
    api_key = st.text_input(
        "OpenWeatherMap API Key",
        value=_secret_key,
        type="password",
        placeholder="Paste your free API key here",
        help="Get a free key at openweathermap.org/api",
    )
    st.caption("Required for live data, location fetch, and comparison.")
    st.divider()
    st.markdown("**AQI Scale Reference**")
    for cat, s in CATEGORY_STYLE.items():
        st.markdown(
            f'<span style="background:{s["bg"]};color:{s["fg"]};'
            f'padding:2px 8px;border-radius:4px;font-size:12px;">'
            f'{s["emoji"]} {cat}</span>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("Smart AQI Predictor 🌍")
st.caption("Predict AQI from pollutant data and compare against live conditions.")
st.divider()

# ---------------------------------------------------------------------------
# City + fetch + location row
# ---------------------------------------------------------------------------
city_col, fetch_col, loc_col = st.columns([3, 1, 1], vertical_alignment="bottom")

with city_col:
    city_input = st.text_input("🏙️ City", placeholder="e.g. Delhi, London, New York")

with fetch_col:
    fetch_clicked = st.button("🌐 Fetch", use_container_width=True,
                              help="Auto-fill from OpenWeatherMap")

with loc_col:
    locate_clicked = st.button("📍 My Location", use_container_width=True,
                               help="Detect via browser GPS")


def _load_live_data(lat: float, lon: float, key: str):
    """Fetch pollution + weather + official AQI and store in session state."""
    data = fetch_pollution_by_coords(lat, lon, key)
    st.session_state.pm25         = data["pm25"]
    st.session_state.pm10         = data["pm10"]
    st.session_state.no2          = data["no2"]
    st.session_state.co           = data["co"]
    st.session_state.o3           = data["o3"]
    st.session_state.fetched_city = data["city"]
    st.session_state.data_source  = "live"

    try:
        st.session_state.live_weather  = fetch_current_weather(lat, lon, key)
    except Exception:
        st.session_state.live_weather  = None

    try:
        st.session_state.live_aqi_data = fetch_official_aqi(lat, lon, key)
    except Exception:
        st.session_state.live_aqi_data = None

    return data["city"]


# --- Geolocation ---
if locate_clicked:
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
        key="geo_js",
    )
    if coords is None:
        st.info("📡 Waiting for browser location permission…")
    elif coords in ("null", False):
        st.error("❌ Location access denied. Enter a city manually.")
        st.session_state.geo_pending = False
    else:
        try:
            lat, lon = float(coords["lat"]), float(coords["lon"])
            st.session_state.geo_lat     = lat
            st.session_state.geo_lon     = lon
            st.session_state.geo_pending = False
            with st.spinner("Fetching live conditions for your location…"):
                if not api_key:
                    st.error("🔑 Add your API key in the sidebar.")
                else:
                    city_name = _load_live_data(lat, lon, api_key)
                    st.success(f"✅ Location detected: **{city_name}**")
        except (TypeError, KeyError):
            st.error("❌ Could not read coordinates. Try again.")
            st.session_state.geo_pending = False

# --- City fetch ---
if fetch_clicked:
    if not city_input.strip():
        st.warning("Enter a city name first.")
    elif not api_key:
        st.error("🔑 Add your API key in the sidebar.")
    else:
        with st.spinner(f"Fetching live data for **{city_input}**…"):
            try:
                from weather_api import _get_coordinates
                lat, lon, _ = _get_coordinates(city_input.strip(), api_key)
                city_name   = _load_live_data(lat, lon, api_key)
                st.success(f"✅ Live data loaded for **{city_name}**")
            except CityNotFoundError as e:
                st.error(f"🔍 {e}")
            except APIError as e:
                st.error(f"🌐 API error: {e}")
            except Exception as e:
                st.error(f"❌ {e}")

# ---------------------------------------------------------------------------
# Live conditions card  (shown whenever we have weather data)
# ---------------------------------------------------------------------------
if st.session_state.live_weather and st.session_state.live_aqi_data:
    w   = st.session_state.live_weather
    aq  = st.session_state.live_aqi_data
    sty = OWM_AQI_STYLE.get(aq["owm_aqi"], {"bg": "#ccc", "fg": "#000", "label": "?"})

    st.markdown(f"### 📍 {st.session_state.fetched_city}")
    wc, aqc = st.columns(2)

    with wc:
        icon_url = f"https://openweathermap.org/img/wn/{w['icon']}@2x.png"
        st.markdown(
            f"""
            <div class="weather-card">
                <div style="display:flex;align-items:center;gap:12px;">
                    <img src="{icon_url}" width="60"/>
                    <div>
                        <div class="weather-temp">{w['temp_c']}°C</div>
                        <div class="weather-desc">{w['description']}</div>
                    </div>
                </div>
                <div style="display:flex;gap:24px;margin-top:14px;font-size:13px;opacity:0.85;">
                    <span>💧 Humidity: {w['humidity']}%</span>
                    <span>💨 Wind: {w['wind_kph']} km/h</span>
                    <span>👁️ Vis: {w['visibility']//1000} km</span>
                </div>
                <div style="font-size:12px;opacity:0.6;margin-top:6px;">
                    Feels like {w['feels_like']}°C
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with aqc:
        st.markdown(
            f"""
            <div class="aqi-card" style="background:{sty['bg']};color:{sty['fg']};height:100%;">
                <div style="font-size:13px;font-weight:600;opacity:0.7;margin-bottom:4px;">
                    LIVE AQI (OpenWeatherMap)
                </div>
                <div class="aqi-number">{aq['owm_aqi']}<span style="font-size:28px;">/5</span></div>
                <div class="aqi-label">{sty['label']}</div>
                <div style="font-size:12px;margin-top:10px;opacity:0.75;">
                    PM2.5 {aq['pm25']} · PM10 {aq['pm10']} · NO₂ {aq['no2']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.divider()

# ---------------------------------------------------------------------------
# Pollutant inputs
# ---------------------------------------------------------------------------
st.markdown("#### 🧪 Pollutant Concentrations")

badge_style = ("background:#d4edda;color:#155724;" if st.session_state.data_source == "live"
               else "background:#e2e3e5;color:#383d41;")
badge_text  = ("🌐 Live data — edit to override" if st.session_state.data_source == "live"
               else "✏️ Manual input")
st.markdown(f'<span class="source-badge" style="{badge_style}">{badge_text}</span>',
            unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    pm25 = st.number_input("PM2.5  (µg/m³)", min_value=0.0, max_value=500.0,
                           value=st.session_state.pm25, format="%.1f", key="input_pm25")
    no2  = st.number_input("NO₂    (µg/m³)", min_value=0.0, max_value=500.0,
                           value=st.session_state.no2,  format="%.1f", key="input_no2")
    o3   = st.number_input("O₃ / Ozone (µg/m³)", min_value=0.0, max_value=500.0,
                           value=st.session_state.o3,   format="%.1f", key="input_o3")
with col2:
    pm10 = st.number_input("PM10   (µg/m³)", min_value=0.0, max_value=500.0,
                           value=st.session_state.pm10, format="%.1f", key="input_pm10")
    co   = st.number_input("CO     (mg/m³)", min_value=0.0, max_value=50.0,
                           value=st.session_state.co,   format="%.2f", key="input_co")

if st.session_state.data_source == "live":
    if st.button("🔄 Clear & enter manually"):
        for k, v in _DEFAULTS.items():
            st.session_state[k] = v
        st.rerun()

st.divider()
predict_btn = st.button("🔍 Predict AQI", use_container_width=True, type="primary")

# ---------------------------------------------------------------------------
# Prediction + comparison
# ---------------------------------------------------------------------------
if predict_btn:
    inputs   = {"pm25": pm25, "pm10": pm10, "no2": no2, "co": co, "o3": o3}
    provided = {k: v for k, v in inputs.items() if v is not None and v > 0}

    if not provided:
        st.error("⚠️ Please enter at least one pollutant value before predicting.")
        st.stop()

    with st.spinner("Analysing air quality data…"):
        try:
            result = predict_aqi(provided)
        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")
            st.stop()

    aqi      = result["aqi"]
    category = result["category"]
    advice   = result["health_advice"]
    style    = CATEGORY_STYLE.get(category, {"bg": "#cccccc", "fg": "#000000", "emoji": "🌫️"})

    display_city = st.session_state.fetched_city or city_input.strip()
    if display_city:
        st.markdown(f"### 📍 Results — {display_city}")

    # -----------------------------------------------------------------------
    # Side-by-side: Model prediction  |  Live AQI comparison
    # -----------------------------------------------------------------------
    pred_col, comp_col = st.columns(2)

    with pred_col:
        st.markdown("##### 🤖 Model Prediction")
        st.markdown(
            f"""
            <div class="aqi-card" style="background:{style['bg']};color:{style['fg']};">
                <div class="aqi-number">{aqi}</div>
                <div class="aqi-label">{style['emoji']} {category}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="advice-box">💡 {advice}</div>',
            unsafe_allow_html=True,
        )

    with comp_col:
        st.markdown("##### 📡 Live AQI (OpenWeatherMap)")
        aq = st.session_state.live_aqi_data

        if aq:
            owm_idx  = aq["owm_aqi"]
            owm_us   = _owm_to_us_aqi(owm_idx)
            sty      = OWM_AQI_STYLE.get(owm_idx, {"bg": "#ccc", "fg": "#000", "label": "?"})

            st.markdown(
                f"""
                <div class="aqi-card" style="background:{sty['bg']};color:{sty['fg']};">
                    <div class="aqi-number">{owm_idx}<span style="font-size:28px;">/5</span></div>
                    <div class="aqi-label">{sty['label']}</div>
                    <div style="font-size:13px;margin-top:8px;opacity:0.75;">
                        ≈ US AQI {owm_us:.0f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Accuracy metrics
            abs_err    = abs(aqi - owm_us)
            pct_err    = (abs_err / owm_us * 100) if owm_us > 0 else 0
            err_color  = _accuracy_color(pct_err)
            match      = "✅ Close match" if pct_err <= 20 else "⚠️ Notable difference"

            st.markdown("##### 📊 Model vs Live Comparison")
            m1, m2, m3 = st.columns(3)
            m1.metric("Model AQI",    f"{aqi:.1f}")
            m2.metric("Live ≈ AQI",   f"{owm_us:.0f}")
            m3.metric("Abs. Error",   f"{abs_err:.1f}")

            st.markdown(
                f"""
                <div class="compare-box">
                    <div style="font-size:13px;color:#555;margin-bottom:6px;">
                        Percentage Error
                    </div>
                    <div style="font-size:28px;font-weight:800;color:{err_color};">
                        {pct_err:.1f}%
                    </div>
                    <div style="font-size:13px;margin-top:4px;">{match}</div>
                    <div style="background:#eee;border-radius:8px;height:8px;margin-top:10px;">
                        <div style="background:{err_color};width:{min(pct_err,100):.0f}%;
                             height:8px;border-radius:8px;"></div>
                    </div>
                    <div style="font-size:11px;color:#888;margin-top:6px;">
                        Note: OWM uses a 1–5 index; US AQI midpoints used for comparison.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("Fetch live data first (🌐 Fetch or 📍 My Location) to see the comparison.")

    st.divider()

    # -----------------------------------------------------------------------
    # Pollutant breakdown
    # -----------------------------------------------------------------------
    st.markdown("#### 📊 Pollutant Values Used")
    label_map = {"pm25": "PM2.5", "pm10": "PM10", "no2": "NO₂", "co": "CO", "o3": "O₃"}
    unit_map  = {"pm25": "µg/m³", "pm10": "µg/m³", "no2": "µg/m³", "co": "mg/m³", "o3": "µg/m³"}
    mcols = st.columns(len(provided))
    for col, (key, val) in zip(mcols, provided.items()):
        with col:
            st.metric(f"{label_map[key]} ({unit_map[key]})", f"{val:.2f}")

    st.divider()

    # -----------------------------------------------------------------------
    # 7-day trend
    # -----------------------------------------------------------------------
    st.markdown("#### 📈 7-Day AQI Trend")

    trend_df  = None
    trend_src = "dummy"
    trend_city = st.session_state.fetched_city or city_input.strip()

    if api_key and trend_city:
        with st.spinner("Loading historical trend…"):
            try:
                history = fetch_historical_pollution(trend_city, days=7, api_key=api_key)
                rows = []
                for day in history:
                    day_inputs = {k: v for k, v in day.items()
                                  if k != "date" and v and v > 0}
                    try:
                        day_aqi = predict_aqi(day_inputs)["aqi"]
                    except Exception:
                        day_aqi = None
                    rows.append({"Date": pd.Timestamp(day["date"]), "AQI": day_aqi})
                trend_df  = pd.DataFrame(rows).dropna()
                trend_src = "live"
            except (APIKeyMissingError, CityNotFoundError, APIError):
                trend_df = None

    if trend_df is None or trend_df.empty:
        trend_df  = _dummy_trend(anchor_aqi=aqi)
        trend_src = "dummy"

    badge = ("🌐 Live historical data" if trend_src == "live"
             else "⚠️ Illustrative data — add API key for real history")
    badge_bg = "#d4edda;color:#155724" if trend_src == "live" else "#fff3cd;color:#856404"
    st.markdown(f'<span class="source-badge" style="background:{badge_bg};">{badge}</span>',
                unsafe_allow_html=True)

    st.altair_chart(_trend_chart(trend_df, predicted_aqi=aqi), use_container_width=True)
