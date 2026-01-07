# Current System Limitations

## 1. Accuracy of Health Warnings (False Positives)
**[RESOLVED 70%]**
- The system now **correctly handles** "False Friends":
  - "Peanut Butter", "Shea Butter", "Cocoa Butter" no longer trigger Dairy warnings.
  - "Coconut Milk", "Almond Milk", "Rice Milk" no longer trigger Dairy warnings.
  - "Eggplant" no longer triggers Egg allergy.
  - "Pineapple" no longer triggers Apple allergy.
- **Residual Risk**: Complex phrasing like "Milk-style coconut beverage" might still be tricky, but main cases are covered.

## 2. Legacy Data (Sodium & Ingredients)
- **Zero Sodium in Old Data**: Foods added to your local database *before* today do not have sodium values. They will not trigger hypertension or sodium-related warnings until re-saved.
- **Missing Ingredients**: Foods created manually often lack detailed ingredient lists. The system falls back to checking the **Food Name**.

## 3. "One-Size-Fits-All" Thresholds
- **Hardcoded Limits**: Warnings (e.g., "High Sodium > 400mg") are based on general health guidelines.
- **Not Personalized**: The thresholds do not adjust based on your specific weight, age, or severity of condition.

## 4. Language Support
- **English Only**: The allergen detection works strictly with English keywords. If a scanned product returns ingredients in French or German, warnings will likely be missed.

## 5. Performance
- **Connection Speed**: Searching OpenFoodFacts + filtering for English + checking 10+ health conditions per item adds latency (1-2 seconds) to search results.
