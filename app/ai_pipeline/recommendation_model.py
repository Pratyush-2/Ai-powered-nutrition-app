from app.schemas import UserProfile, Food

def predict_food_recommendation(user: UserProfile, food: Food) -> str:
    """
    This is a placeholder for a trained Random Forest model.
    It simulates the model's output by returning a "recommend" or "not recommend" decision.
    """
    # In a real implementation, you would use a trained model to make a prediction
    # based on the user's profile and the food's nutritional information.
    # For this MVP, we'll use a simple heuristic.
    if food.calories < 500 and food.protein > 10:
        return "recommend"
    else:
        return "not recommend"
