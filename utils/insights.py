"""
Smart Insights Engine
Generates intelligent insights from AQI trends and comparisons
"""

from typing import Dict, List, Optional
import pandas as pd


def generate_comparison_insight(predicted_aqi: float, real_aqi: float) -> Dict[str, str]:
    """Generate insight comparing predicted vs real AQI."""
    diff = predicted_aqi - real_aqi
    abs_diff = abs(diff)
    pct_diff = (abs_diff / real_aqi * 100) if real_aqi > 0 else 0
    
    if abs_diff <= 10:
        accuracy = "excellent"
        emoji = "🎯"
        color = "#00c853"
    elif abs_diff <= 25:
        accuracy = "good"
        emoji = "✅"
        color = "#64dd17"
    elif abs_diff <= 50:
        accuracy = "moderate"
        emoji = "⚠️"
        color = "#ffd600"
    else:
        accuracy = "needs improvement"
        emoji = "❌"
        color = "#ff6d00"
    
    if diff > 0:
        direction = "higher"
        reason = "Model may be overestimating pollution levels"
    elif diff < 0:
        direction = "lower"
        reason = "Model may be underestimating pollution levels"
    else:
        direction = "exactly matching"
        reason = "Perfect prediction!"
    
    return {
        "emoji": emoji,
        "accuracy": accuracy,
        "color": color,
        "difference": abs_diff,
        "percentage": pct_diff,
        "direction": direction,
        "reason": reason,
        "message": f"{emoji} Prediction is {abs_diff:.1f} points {direction} than real-time AQI ({accuracy} accuracy)"
    }


def generate_trend_insights(historical_data: List[Dict]) -> List[str]:
    """Analyze historical data and generate insights."""
    if not historical_data or len(historical_data) < 2:
        return ["Insufficient data for trend analysis"]
    
    insights = []
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(historical_data)
    
    # Trend direction
    first_aqi = df.iloc[0].get("aqi", 0)
    last_aqi = df.iloc[-1].get("aqi", 0)
    
    if last_aqi > first_aqi * 1.2:
        insights.append("📈 Air quality is significantly worsening over the past week")
    elif last_aqi < first_aqi * 0.8:
        insights.append("📉 Air quality is improving compared to last week")
    else:
        insights.append("➡️ Air quality has been relatively stable")
    
    # Volatility
    if "aqi" in df.columns:
        std_dev = df["aqi"].std()
        if std_dev > 30:
            insights.append("⚡ High volatility detected - AQI fluctuates significantly")
        elif std_dev < 10:
            insights.append("🔒 Low volatility - AQI remains consistent")
    
    # Peak detection
    if "aqi" in df.columns:
        max_aqi = df["aqi"].max()
        max_date = df.loc[df["aqi"].idxmax(), "date"]
        if max_aqi > 150:
            insights.append(f"🚨 Peak pollution detected on {max_date} (AQI: {max_aqi:.0f})")
    
    # PM2.5 dominance
    if "pm25" in df.columns:
        avg_pm25 = df["pm25"].mean()
        if avg_pm25 > 35:
            insights.append("💨 PM2.5 is the primary pollutant - likely from vehicle emissions or wildfires")
    
    return insights


def generate_weather_impact_insight(aqi: float, temp: float, humidity: int) -> Optional[str]:
    """Generate insight about weather impact on AQI."""
    insights = []
    
    if temp > 30 and aqi > 100:
        insights.append("🌡️ High temperature may be increasing ground-level ozone formation")
    
    if humidity > 80 and aqi > 100:
        insights.append("💧 High humidity can trap pollutants near the ground")
    
    if temp < 10 and aqi > 100:
        insights.append("❄️ Cold air traps pollution closer to the surface (temperature inversion)")
    
    if humidity < 30 and aqi > 100:
        insights.append("🏜️ Low humidity increases dust and particulate matter")
    
    return " | ".join(insights) if insights else None


def generate_daily_summary(aqi: float, category: str, weather: Dict) -> str:
    """Generate a human-friendly daily summary."""
    temp = weather.get("temp_c", 0)
    desc = weather.get("description", "")
    
    if aqi <= 50:
        return f"🌟 Excellent day! {desc} with {temp}°C. Perfect for outdoor activities."
    elif aqi <= 100:
        return f"😊 Good day overall. {desc} with {temp}°C. Enjoy outdoor time with minor precautions."
    elif aqi <= 150:
        return f"⚠️ Moderate air quality. {desc} with {temp}°C. Sensitive groups should limit prolonged outdoor exposure."
    elif aqi <= 200:
        return f"😷 Unhealthy air quality. {desc} with {temp}°C. Everyone should reduce outdoor activities."
    elif aqi <= 300:
        return f"🚨 Very unhealthy conditions. {desc} with {temp}°C. Avoid going outside."
    else:
        return f"☠️ HAZARDOUS! {desc} with {temp}°C. Emergency conditions - stay indoors!"


def get_pollutant_breakdown(pollutants: Dict[str, float]) -> List[Dict]:
    """Rank pollutants by contribution."""
    # Normalize to percentage contribution
    total = sum(pollutants.values())
    if total == 0:
        return []
    
    breakdown = []
    for name, value in pollutants.items():
        pct = (value / total) * 100
        breakdown.append({
            "name": name.upper(),
            "value": value,
            "percentage": round(pct, 1),
            "emoji": _get_pollutant_emoji(name)
        })
    
    return sorted(breakdown, key=lambda x: x["percentage"], reverse=True)


def _get_pollutant_emoji(pollutant: str) -> str:
    """Get emoji for pollutant type."""
    mapping = {
        "pm25": "🔴",
        "pm10": "🟠",
        "no2": "🟡",
        "o3": "🔵",
        "co": "⚫",
        "so2": "🟣"
    }
    return mapping.get(pollutant.lower(), "⚪")


def generate_notification_message(aqi: float, prev_aqi: Optional[float] = None) -> Optional[str]:
    """Generate notification-style message."""
    if aqi > 150:
        return f"⚠️ ALERT: AQI is {aqi:.0f} (Unhealthy). Limit outdoor activities."
    
    if prev_aqi and aqi > prev_aqi * 1.3:
        return f"📈 Air quality worsening: AQI increased from {prev_aqi:.0f} to {aqi:.0f}"
    
    if prev_aqi and aqi < prev_aqi * 0.7:
        return f"📉 Good news: AQI improved from {prev_aqi:.0f} to {aqi:.0f}"
    
    return None
