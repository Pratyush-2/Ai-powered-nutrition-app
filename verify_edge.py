import sys
import os
sys.path.append(os.getcwd())
try:
    from app.ai_pipeline.nutrition_engine import nutrition_engine
except ImportError:
    # Handle direct execution from different cwd
    sys.path.append(os.path.dirname(os.getcwd()))
    from app.ai_pipeline.nutrition_engine import nutrition_engine

# Mock User
user_features = {"age": 30, "activity_level": 2, "bmi": 24.0}
user_goals = ["weight_loss"] # Strict goal

def test_food(name, features):
    # Ensure name is in features as expected by new logic
    features["food_name"] = name
    
    print(f"\n--- Testing: {name} ---")
    print(f"Input: {features}")
    
    result = nutrition_engine.calculate_nutrition_score(features, user_features, user_goals)
    
    status = "✅ RECOMMENDED" if result['recommended'] else "❌ NOT RECOMMENDED"
    print(f"Result: {status} (Score: {result['score']})")
    print(f"Reasoning: {result['reasoning']}")
    return result['recommended']

# 1. Ghost Cake (The Problem Case)
# If Logic Works: Estimator sets Sugar=25 -> Veto -> Failed.
test_food("Chocolate Cake", {"calories": 300, "protein": 4, "sugar": 0, "fat": 15, "carbohydrates": 40})

# 2. Real Cake (Control)
# Sugar=25 -> Veto -> Failed.
test_food("Real Cake", {"calories": 300, "protein": 4, "sugar": 25, "fat": 15, "carbohydrates": 40})

# 3. Butter (Healthy Fat Case)
# Fat=80, Sugar=0 -> Healthy Fat Bonus -> Passed.
test_food("Butter", {"calories": 717, "protein": 0.8, "sugar": 0.06, "fat": 81, "carbohydrates": 0.06})

# 4. Orange (Fruit Case)
# Sugar=9, Fiber=0(Missing) -> Estimator sets Fiber=3 -> Passed.
test_food("Fresh Orange", {"calories": 47, "protein": 0.9, "sugar": 9, "fat": 0.1, "carbohydrates": 12})

# 5. Avocado (Healthy Fat)
test_food("Avocado", {"calories": 160, "protein": 2, "sugar": 0.7, "fat": 15, "carbohydrates": 9})

# 6. Soda (Zero Sugar?) 
# Name Veto should catch it.
test_food("Cola Soda", {"calories": 140, "protein": 0, "sugar": 0, "fat": 0, "carbohydrates": 39})
