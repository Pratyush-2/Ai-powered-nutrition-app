# Recommendation System Changes - Verification Guide

## What Was Changed

### 1. `app/ai_pipeline/nutrition_engine.py`
- **Data Estimation** (Lines 97-119): If sugar is 0 but food name contains "cake", "candy", etc., it estimates sugar = 25g
- **Hard Veto Rules** (Lines 197-218):
  - Sugar > 20g AND fiber < 3g → NOT RECOMMENDED
  - Sugar > 15g AND protein < 5g → NOT RECOMMENDED  
  - Name contains "cake/candy/soda" AND sugar > 10g → NOT RECOMMENDED
- **Healthy Fat Bonus** (Lines 164-174): High fat + low sugar foods (butter, nuts) get bonus points

### 2. `app/services/food_search.py`
- Added timeout handling to prevent server crashes
- Timeout set to 4.0 seconds for OpenFoodFacts API

### 3. `app/ai/ai_routes.py`
- Added `food_name` to `food_features` dict so nutrition_engine can use it

## How to Verify It's Working

### Test 1: Backend Logic (Direct Test)
Run this in PowerShell from project root:
```powershell
python -c "from app.ai_pipeline.nutrition_engine import nutrition_engine; print(nutrition_engine.calculate_nutrition_score({'food_name': 'cake', 'calories': 300, 'protein': 4, 'sugar': 25, 'fat': 15, 'carbohydrates': 40, 'fiber': 1}, {'age': 30, 'activity_level': 2, 'bmi': 24}, [])['recommended'])"
```
Expected output: `False`

### Test 2: API Endpoint Test
```powershell
# First get a token (replace with your credentials)
$response = Invoke-RestMethod -Uri "http://localhost:8000/token" -Method Post -Body @{username="your_email"; password="your_password"} -ContentType "application/x-www-form-urlencoded"
$token = $response.access_token

# Test classification
$headers = @{Authorization = "Bearer $token"}
$body = @{food_name = "Chocolate Cake"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8000/ai/classify/" -Method Post -Headers $headers -Body $body -ContentType "application/json"
```

### Test 3: App Behavior
1. Hot restart Flutter app (`R`)
2. Search for "Chocolate Cake"
3. Click on a result
4. Check if it shows "Not Recommended"

## Common Issues

### Issue: Still shows "Recommended"
**Possible causes:**
1. App is using cached data - try full restart
2. App isn't calling `/ai/classify/` endpoint
3. The specific product has different nutritional data than expected

### Issue: Server crashes with 500 error
**Possible causes:**
1. Syntax error in food_search.py - check logs
2. Database connection pool exhausted - restart server

### Issue: OpenFoodFacts timeouts
**This is normal** - the API is slow. The app will fall back to local database.

## Rollback Instructions

If you want to revert all changes:
```powershell
git checkout app/ai_pipeline/nutrition_engine.py
git checkout app/services/food_search.py  
git checkout app/ai/ai_routes.py
git checkout app/schemas.py
```

Then restart the server.
