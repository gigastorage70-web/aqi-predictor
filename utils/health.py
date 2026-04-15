"""
Health Advisory Engine
Generates smart health recommendations based on AQI + weather conditions
"""

from typing import Dict, List


def get_aqi_category(aqi: float) -> Dict[str, str]:
    """Categorize AQI with color, emoji, and label."""
    if aqi <= 50:
        return {
            "category": "Good",
            "color": "#00e400",
            "text_color": "#000000",
            "emoji": "😊",
            "level": 1
        }
    elif aqi <= 100:
        return {
            "category": "Moderate",
            "color": "#ffff00",
            "text_color": "#000000",
            "emoji": "😐",
            "level": 2
        }
    elif aqi <= 150:
        return {
            "category": "Unhealthy for Sensitive Groups",
            "color": "#ff7e00",
            "text_color": "#000000",
            "emoji": "😷",
            "level": 3
        }
    elif aqi <= 200:
        return {
            "category": "Unhealthy",
            "color": "#ff0000",
            "text_color": "#ffffff",
            "emoji": "🤢",
            "level": 4
        }
    elif aqi <= 300:
        return {
            "category": "Very Unhealthy",
            "color": "#8f3f97",
            "text_color": "#ffffff",
            "emoji": "🚨",
            "level": 5
        }
    else:
        return {
            "category": "Hazardous",
            "color": "#7e0023",
            "text_color": "#ffffff",
            "emoji": "☠️",
            "level": 6
        }


def generate_health_advice(aqi: float, temp_c: float = None, 
                          humidity: int = None) -> Dict[str, any]:
    """
    Generate comprehensive health recommendations based on AQI + weather.
    
    Returns dict with:
        - general_advice: str
        - precautions: List[str]
        - risk_groups: List[str]
        - activities: Dict[str, str]
    """
    category = get_aqi_category(aqi)
    level = category["level"]
    
    advice = {
        "general_advice": "",
        "precautions": [],
        "risk_groups": [],
        "activities": {},
        "health_risks": []
    }
    
    # Base AQI advice
    if level == 1:  # Good
        advice["general_advice"] = "Air quality is excellent. Perfect day for outdoor activities!"
        advice["activities"] = {
            "outdoor_exercise": "✅ Recommended",
            "windows_open": "✅ Safe",
            "outdoor_events": "✅ Ideal"
        }
    
    elif level == 2:  # Moderate
        advice["general_advice"] = "Air quality is acceptable. Most people can enjoy outdoor activities."
        advice["precautions"] = [
            "Unusually sensitive individuals should limit prolonged outdoor exertion"
        ]
        advice["risk_groups"] = ["People with respiratory conditions"]
        advice["activities"] = {
            "outdoor_exercise": "✅ Generally safe",
            "windows_open": "✅ Safe",
            "outdoor_events": "⚠️ Monitor sensitive individuals"
        }
    
    elif level == 3:  # Unhealthy for Sensitive Groups
        advice["general_advice"] = "Sensitive groups should reduce prolonged outdoor exposure."
        advice["precautions"] = [
            "Wear N95 mask if you're in a sensitive group",
            "Limit outdoor exercise duration",
            "Keep windows closed during peak pollution hours"
        ]
        advice["risk_groups"] = [
            "Children and elderly",
            "People with heart or lung disease",
            "Pregnant women"
        ]
        advice["activities"] = {
            "outdoor_exercise": "⚠️ Limit for sensitive groups",
            "windows_open": "⚠️ Keep closed during peak hours",
            "outdoor_events": "⚠️ Reduce exposure time"
        }
        advice["health_risks"] = ["Respiratory irritation", "Breathing discomfort"]
    
    elif level == 4:  # Unhealthy
        advice["general_advice"] = "Everyone should reduce prolonged outdoor exertion. Stay indoors when possible."
        advice["precautions"] = [
            "Wear N95 mask outdoors",
            "Avoid outdoor exercise",
            "Keep all windows closed",
            "Use air purifiers indoors",
            "Stay hydrated"
        ]
        advice["risk_groups"] = [
            "Everyone, especially sensitive groups",
            "Children should avoid outdoor play",
            "Elderly should stay indoors"
        ]
        advice["activities"] = {
            "outdoor_exercise": "❌ Not recommended",
            "windows_open": "❌ Keep closed",
            "outdoor_events": "❌ Postpone if possible"
        }
        advice["health_risks"] = [
            "Increased respiratory symptoms",
            "Aggravation of heart/lung disease",
            "Breathing difficulties"
        ]
    
    elif level == 5:  # Very Unhealthy
        advice["general_advice"] = "Health alert! Everyone should avoid all outdoor exertion."
        advice["precautions"] = [
            "Stay indoors with windows closed",
            "Use air purifiers on high setting",
            "Wear N95 mask if you must go outside",
            "Avoid all physical exertion",
            "Monitor health symptoms closely"
        ]
        advice["risk_groups"] = [
            "Everyone is at risk",
            "Immediate danger for sensitive groups"
        ]
        advice["activities"] = {
            "outdoor_exercise": "❌ Dangerous",
            "windows_open": "❌ Keep sealed",
            "outdoor_events": "❌ Cancel"
        }
        advice["health_risks"] = [
            "Serious respiratory effects",
            "Cardiovascular stress",
            "Emergency room visits may increase"
        ]
    
    else:  # Hazardous
        advice["general_advice"] = "EMERGENCY CONDITIONS! Stay indoors. Avoid all outdoor activity."
        advice["precautions"] = [
            "🚨 Do not go outside unless absolutely necessary",
            "Seal windows and doors",
            "Run air purifiers continuously",
            "Wear N95 mask even indoors if air quality is poor",
            "Seek medical attention if experiencing symptoms"
        ]
        advice["risk_groups"] = [
            "EVERYONE is at serious risk",
            "Evacuate if possible"
        ]
        advice["activities"] = {
            "outdoor_exercise": "🚨 DANGEROUS",
            "windows_open": "🚨 NEVER",
            "outdoor_events": "🚨 EMERGENCY - CANCEL ALL"
        }
        advice["health_risks"] = [
            "Severe respiratory distress",
            "Heart attacks",
            "Premature death in vulnerable populations"
        ]
    
    # Weather-based adjustments
    if temp_c is not None and humidity is not None:
        weather_advice = []
        
        # High temperature + poor AQI
        if temp_c > 32 and level >= 3:
            weather_advice.append("🌡️ High heat + poor air quality increases health risks")
            advice["health_risks"].append("Heat exhaustion risk")
            advice["precautions"].append("Stay in air-conditioned spaces")
        
        # High humidity + poor AQI
        if humidity > 70 and level >= 3:
            weather_advice.append("💧 High humidity makes breathing more difficult")
            advice["health_risks"].append("Increased breathing discomfort")
        
        # Cold + poor AQI
        if temp_c < 10 and level >= 3:
            weather_advice.append("❄️ Cold air + pollution can irritate airways")
            advice["precautions"].append("Cover nose and mouth if going outside")
        
        if weather_advice:
            advice["weather_impact"] = weather_advice
    
    return advice


def get_pollutant_info(pollutant: str, value: float) -> Dict[str, str]:
    """Get health impact info for specific pollutants."""
    
    pollutant_data = {
        "PM2.5": {
            "name": "Fine Particulate Matter (PM2.5)",
            "source": "Vehicle exhaust, industrial emissions, wildfires",
            "health_impact": "Penetrates deep into lungs and bloodstream",
            "safe_limit": 12.0,
            "unit": "µg/m³"
        },
        "PM10": {
            "name": "Coarse Particulate Matter (PM10)",
            "source": "Dust, pollen, mold, construction sites",
            "health_impact": "Irritates airways, aggravates asthma",
            "safe_limit": 50.0,
            "unit": "µg/m³"
        },
        "NO2": {
            "name": "Nitrogen Dioxide",
            "source": "Vehicle emissions, power plants",
            "health_impact": "Inflames airways, reduces lung function",
            "safe_limit": 40.0,
            "unit": "µg/m³"
        },
        "O3": {
            "name": "Ground-level Ozone",
            "source": "Formed by sunlight + pollutants",
            "health_impact": "Damages lung tissue, worsens asthma",
            "safe_limit": 100.0,
            "unit": "µg/m³"
        },
        "CO": {
            "name": "Carbon Monoxide",
            "source": "Vehicle exhaust, incomplete combustion",
            "health_impact": "Reduces oxygen delivery to organs",
            "safe_limit": 4.0,
            "unit": "mg/m³"
        }
    }
    
    info = pollutant_data.get(pollutant, {})
    if not info:
        return {}
    
    status = "✅ Safe" if value <= info["safe_limit"] else "⚠️ Elevated"
    
    return {
        **info,
        "current_value": value,
        "status": status,
        "percentage_of_limit": round((value / info["safe_limit"]) * 100, 1)
    }
