# Fresh Food Mapper - Provides nutritional data for common fresh foods
FRESH_FOODS = {
    "apple": {
        "product_name": "Fresh Apple",
        "categories": "Fresh fruits, Fruits",
        "nutriments": {
            "energy-kcal": 52,
            "energy-kcal_100g": 52,
            "energy-kj": 218,
            "energy-kj_100g": 218,
            "carbohydrates": 14.0,
            "carbohydrates_100g": 14.0,
            "sugars": 10.4,
            "sugars_100g": 10.4,
            "fiber": 2.4,
            "fiber_100g": 2.4,
            "proteins": 0.3,
            "proteins_100g": 0.3,
            "fat": 0.2,
            "fat_100g": 0.2,
            "saturated-fat": 0.03,
            "saturated-fat_100g": 0.03,
            "sodium": 1,
            "sodium_100g": 1,
            "salt": 0.0025,
            "salt_100g": 0.0025,
        }
    },
    "banana": {
        "product_name": "Fresh Banana", 
        "categories": "Fresh fruits, Fruits",
        "nutriments": {
            "energy-kcal": 89,
            "energy-kcal_100g": 89,
            "energy-kj": 371,
            "energy-kj_100g": 371,
            "carbohydrates": 22.8,
            "carbohydrates_100g": 22.8,
            "sugars": 12.2,
            "sugars_100g": 12.2,
            "fiber": 2.6,
            "fiber_100g": 2.6,
            "proteins": 1.1,
            "proteins_100g": 1.1,
            "fat": 0.3,
            "fat_100g": 0.3,
            "saturated-fat": 0.11,
            "saturated-fat_100g": 0.11,
            "sodium": 1,
            "sodium_100g": 1,
            "salt": 0.0025,
            "salt_100g": 0.0025,
        }
    }
}

def get_fresh_food_data(food_name):
    return FRESH_FOODS.get(food_name.lower())

def create_product_from_fresh_data(fresh_data):
    return {"product": fresh_data, "status": 1}