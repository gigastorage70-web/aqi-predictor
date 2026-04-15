# 🧪 Testing Guide - AQI Intelligence

## Pre-Launch Testing Checklist

### 1. Local Environment Setup

```bash
# Install dependencies
pip install -r requirements_production.txt

# Set API key
export OPENWEATHER_API_KEY="your_key"

# Run app
streamlit run app_production.py
```

### 2. Core Functionality Tests

#### ✅ Model Loading
- [ ] App starts without errors
- [ ] Model loads on first prediction
- [ ] Subsequent predictions use cached model
- [ ] No "file not found" errors

**Test:**
```python
# In Python console
from predictor import predict_aqi
result = predict_aqi({"pm25": 95, "pm10": 180, "no2": 45, "co": 1.2, "o3": 60})
print(result)  # Should return dict with aqi, category, health_advice
```

#### ✅ API Integration
- [ ] City search works
- [ ] Coordinates resolve correctly
- [ ] Pollution data fetches
- [ ] Weather data fetches
- [ ] Historical data loads
- [ ] Caching works (check logs)

**Test Cities:**
- Delhi, India (high pollution)
- London, UK (moderate)
- Reykjavik, Iceland (low pollution)
- Invalid city (should show error)

#### ✅ Geolocation
- [ ] "My Location" button appears
- [ ] Browser prompts for permission
- [ ] Coordinates detected correctly
- [ ] City name resolved from coords
- [ ] Graceful handling of denied permission

**Test:**
1. Click "My Location"
2. Allow permission
3. Verify city name appears
4. Check data loads

#### ✅ Dual AQI Display
- [ ] ML prediction shows
- [ ] Real-time AQI shows
- [ ] Comparison insight generates
- [ ] Accuracy metrics display
- [ ] Color coding correct

**Test:**
- Compare predicted vs real for multiple cities
- Verify difference calculation
- Check percentage error

#### ✅ Health Advisory
- [ ] General advice displays
- [ ] Precautions list correct for AQI level
- [ ] Risk groups identified
- [ ] Activity recommendations show
- [ ] Weather impact considered

**Test AQI Levels:**
- Good (0-50)
- Moderate (51-100)
- Unhealthy for Sensitive Groups (101-150)
- Unhealthy (151-200)
- Very Unhealthy (201-300)
- Hazardous (301+)

#### ✅ Pollutant Breakdown
- [ ] All pollutants display
- [ ] Values correct
- [ ] Percentage bars render
- [ ] Health impact info shows
- [ ] Safe limit comparison works

#### ✅ Historical Trends
- [ ] 7-day chart renders
- [ ] Both predicted and real lines show
- [ ] Dates formatted correctly
- [ ] Tooltips work
- [ ] Trend insights generate

### 3. UI/UX Tests

#### ✅ Mobile Responsiveness
- [ ] Layout adapts to mobile screen
- [ ] Text readable on small screens
- [ ] Buttons tap-friendly (min 44x44px)
- [ ] No horizontal scrolling
- [ ] Charts scale properly

**Test Devices:**
- iPhone (Safari)
- Android (Chrome)
- iPad (Safari)
- Desktop (Chrome, Firefox, Safari)

#### ✅ Loading States
- [ ] Spinners show during API calls
- [ ] Loading messages clear
- [ ] No blank screens
- [ ] Smooth transitions

#### ✅ Error Handling
- [ ] Invalid city shows friendly error
- [ ] API failure handled gracefully
- [ ] Missing API key shows clear message
- [ ] Network errors don't crash app

**Test Scenarios:**
1. Enter gibberish city name
2. Disconnect internet mid-fetch
3. Remove API key
4. Enter special characters in city field

### 4. Performance Tests

#### ✅ Load Time
- [ ] Initial load < 3 seconds
- [ ] Model loads < 1 second (cached)
- [ ] API calls < 2 seconds
- [ ] Chart renders < 1 second

**Measure:**
```bash
# Use browser DevTools Network tab
# Check "Finish" time
```

#### ✅ Caching
- [ ] Model cached after first load
- [ ] API responses cached (5-10 min)
- [ ] No redundant API calls
- [ ] Cache invalidates correctly

**Test:**
1. Load app
2. Search city
3. Refresh page
4. Search same city
5. Check network tab - should use cache

#### ✅ Memory Usage
- [ ] No memory leaks
- [ ] Stable after multiple searches
- [ ] Charts don't accumulate

**Monitor:**
```bash
# Browser DevTools → Performance → Memory
# Run for 5 minutes, check for growth
```

### 5. Data Accuracy Tests

#### ✅ Prediction Accuracy
- [ ] Predictions within reasonable range (0-500)
- [ ] Matches real AQI trend
- [ ] No negative values
- [ ] No NaN/Infinity values

**Test:**
```python
# Compare predictions for known cities
cities = ["Delhi", "London", "Tokyo", "New York"]
for city in cities:
    # Fetch and compare
    # Difference should be < 50 AQI points typically
```

#### ✅ Health Advice Accuracy
- [ ] Advice matches AQI level
- [ ] Weather factors considered
- [ ] Risk groups appropriate
- [ ] Activities recommendations logical

**Verify:**
- AQI 50 → "Enjoy outdoor activities"
- AQI 200 → "Avoid outdoor exertion"
- High temp + high AQI → Heat warning

### 6. Security Tests

#### ✅ API Key Protection
- [ ] Key not in source code
- [ ] Key not in browser console
- [ ] Key not in network requests (query params)
- [ ] Secrets file in .gitignore

**Check:**
```bash
# Search codebase
grep -r "OPENWEATHER_API_KEY" --exclude-dir=.git
# Should only find in secrets.toml and config examples
```

#### ✅ Input Validation
- [ ] City input sanitized
- [ ] No SQL injection possible
- [ ] No XSS vulnerabilities
- [ ] No code injection

**Test:**
```
# Try malicious inputs
<script>alert('xss')</script>
'; DROP TABLE users; --
../../../etc/passwd
```

### 7. Accessibility Tests

#### ✅ Screen Reader
- [ ] All images have alt text
- [ ] Buttons have labels
- [ ] Form inputs labeled
- [ ] Headings hierarchical

**Test with:**
- NVDA (Windows)
- VoiceOver (Mac/iOS)
- TalkBack (Android)

#### ✅ Keyboard Navigation
- [ ] Tab through all elements
- [ ] Enter activates buttons
- [ ] No keyboard traps
- [ ] Focus visible

**Test:**
- Navigate entire app with Tab/Shift+Tab
- Activate all buttons with Enter/Space

#### ✅ Color Contrast
- [ ] Text readable on backgrounds
- [ ] WCAG AA compliance (4.5:1)
- [ ] Color not sole indicator

**Check:**
- Use browser DevTools → Lighthouse → Accessibility
- Target score: 90+

### 8. Browser Compatibility

#### ✅ Desktop Browsers
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

#### ✅ Mobile Browsers
- [ ] Chrome Mobile
- [ ] Safari iOS
- [ ] Samsung Internet
- [ ] Firefox Mobile

### 9. PWA Tests

#### ✅ Installability
- [ ] "Add to Home Screen" prompt shows
- [ ] Icon appears on home screen
- [ ] App opens in standalone mode
- [ ] Splash screen displays

**Test:**
1. Open in mobile browser
2. Tap Share → Add to Home Screen
3. Open from home screen
4. Verify standalone mode (no browser UI)

#### ✅ Offline Behavior
- [ ] Graceful offline message
- [ ] Cached data accessible
- [ ] No crashes when offline

### 10. Load Testing

#### ✅ Concurrent Users
- [ ] 10 simultaneous users
- [ ] 50 simultaneous users
- [ ] 100 simultaneous users

**Tools:**
- Apache JMeter
- Locust
- k6

**Test Script (k6):**
```javascript
import http from 'k6/http';
import { check } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 10 },
    { duration: '3m', target: 50 },
    { duration: '1m', target: 0 },
  ],
};

export default function () {
  let res = http.get('https://your-app.streamlit.app');
  check(res, { 'status is 200': (r) => r.status === 200 });
}
```

### 11. Regression Testing

After any code changes, re-run:

1. Core functionality tests
2. UI/UX tests
3. Performance tests
4. Data accuracy tests

### 12. User Acceptance Testing

#### ✅ Real User Scenarios
- [ ] New user can find their city
- [ ] User understands AQI meaning
- [ ] Health advice is actionable
- [ ] Charts are interpretable
- [ ] App feels fast and responsive

**Test with:**
- 5-10 real users
- Different age groups
- Different tech literacy levels

### Test Results Template

```markdown
## Test Run: [Date]

### Environment
- Browser: Chrome 120
- Device: iPhone 14
- Network: 4G

### Results
- ✅ Model loading: PASS
- ✅ API integration: PASS
- ❌ Geolocation: FAIL (permission denied)
- ✅ Health advisory: PASS
- ⚠️ Chart rendering: SLOW (3.5s)

### Issues Found
1. Geolocation doesn't work on iOS Safari
2. Chart takes too long to render on mobile

### Action Items
- [ ] Fix iOS geolocation
- [ ] Optimize chart rendering
- [ ] Add loading skeleton for charts
```

## Automated Testing (Future)

### Unit Tests
```python
# test_predictor.py
def test_predict_aqi():
    result = predict_aqi({"pm25": 95, "pm10": 180})
    assert "aqi" in result
    assert 0 <= result["aqi"] <= 500
```

### Integration Tests
```python
# test_api.py
def test_fetch_pollution():
    data = fetch_current_pollution(28.6, 77.2, api_key)
    assert "pm25" in data
    assert data["pm25"] >= 0
```

### E2E Tests (Selenium)
```python
# test_e2e.py
def test_city_search():
    driver.get("http://localhost:8501")
    driver.find_element_by_id("city_input").send_keys("Delhi")
    driver.find_element_by_id("fetch_btn").click()
    assert "Delhi" in driver.page_source
```

## Continuous Testing

### Pre-Commit Hooks
```bash
# .git/hooks/pre-commit
#!/bin/bash
python -m pytest tests/
python -m flake8 .
```

### CI/CD Pipeline (GitHub Actions)
```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements_production.txt
      - run: pytest tests/
```

---

✅ All tests passing? Ready to deploy!
