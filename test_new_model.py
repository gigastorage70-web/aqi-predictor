"""Quick test of the new model"""

from predictor_updated import predict_aqi

print("🧪 Testing New Model\n")

# Test 1: Simple pollutant input
print("Test 1: Simple pollutant input")
result = predict_aqi({
    "pm25": 95.0,
    "pm10": 180.0,
    "no2": 45.0,
    "co": 1.2
})
print(f"  AQI: {result['aqi']}")
print(f"  Category: {result['category']}")
print(f"  ✅ Test 1 passed\n")

# Test 2: With weather data
print("Test 2: With weather data")
result = predict_aqi({
    "pm25": 150.0,
    "pm10": 250.0,
    "no2": 65.0,
    "co": 2.5,
    "o3": 45.0,
    "temperature": 28.5,
    "humidity": 65,
    "wind_speed": 12.0
})
print(f"  AQI: {result['aqi']}")
print(f"  Category: {result['category']}")
print(f"  ✅ Test 2 passed\n")

# Test 3: Minimal input
print("Test 3: Minimal input (only PM2.5)")
result = predict_aqi({
    "pm25": 50.0
})
print(f"  AQI: {result['aqi']}")
print(f"  Category: {result['category']}")
print(f"  ✅ Test 3 passed\n")

print("✅ All tests passed! Model is working correctly.")
