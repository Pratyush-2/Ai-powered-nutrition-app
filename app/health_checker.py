from typing import List, Dict, Any
from . import models, schemas

class HealthChecker:
    """Service to check food safety based on user's health profile"""
    
    # Common allergen keywords
    ALLERGEN_KEYWORDS = {
        "peanuts": ["peanut", "groundnut"],
        "tree_nuts": ["almond", "cashew", "walnut", "pistachio", "hazelnut", "pecan"],
        "dairy": ["milk", "cheese", "butter", "cream", "yogurt", "whey", "casein", "lactose"],
        "eggs": ["egg", "albumin", "mayonnaise"],
        "soy": ["soy", "tofu", "edamame", "tempeh"],
        "wheat": ["wheat", "flour", "bread", "pasta"],
        "gluten": ["wheat", "barley", "rye", "gluten"],
        "shellfish": ["shrimp", "crab", "lobster", "prawn", "crayfish"],
        "fish": ["fish", "salmon", "tuna", "cod", "halibut"],
        "sesame": ["sesame", "tahini"],
    }
    
    # Health condition nutritional triggers (per 100g)
    CONDITION_TRIGGERS = {
        "diabetes": {
            "high_sugar": 15,  # g per 100g
            "high_carbs": 50,  # g per 100g
        },
        "high_cholesterol": {
            "high_saturated_fat": 5,  # g per 100g
            "high_total_fat": 20,  # g per 100g
        },
        "hypertension": {
            "high_sodium": 400,  # mg per 100g (if we add sodium tracking)
        },
        "heart_disease": {
            "high_saturated_fat": 5,
            "high_total_fat": 20,
        },
        "kidney_disease": {
            "high_protein": 20,  # g per 100g
            "high_sodium": 300,
        },
    }
    
    def check_food_safety(
        self, 
        food: models.Food, 
        health_profile: models.UserHealthProfile,
        quantity: float = 100.0
    ) -> List[schemas.HealthWarning]:
        """
        Check if food is safe for user based on their health profile
        
        Args:
            food: Food object to check
            health_profile: User's health profile
            quantity: Quantity in grams (default 100g)
            
        Returns:
            List of health warnings
        """
        warnings = []
        
        # Calculate actual nutrition values based on quantity
        multiplier = quantity / 100.0
        actual_calories = food.calories * multiplier
        actual_protein = food.protein * multiplier
        actual_carbs = food.carbs * multiplier
        actual_fats = food.fats * multiplier
        
        # Check allergies (CRITICAL)
        for allergy in health_profile.allergies:
            if self._contains_allergen(food.name, allergy):
                warnings.append(schemas.HealthWarning(
                    type="allergy",
                    severity="critical",
                    message=f"⚠️ ALLERGY ALERT: Contains {allergy}!",
                    icon="🚨"
                ))
        
        # Check lactose intolerance
        if health_profile.lactose_intolerant:
            if self._contains_allergen(food.name, "dairy"):
                warnings.append(schemas.HealthWarning(
                    type="intolerance",
                    severity="warning",
                    message="Contains dairy/lactose",
                    icon="⚠️"
                ))
        
        # Check gluten intolerance
        if health_profile.gluten_intolerant or health_profile.has_celiac:
            if self._contains_allergen(food.name, "gluten"):
                severity = "critical" if health_profile.has_celiac else "warning"
                warnings.append(schemas.HealthWarning(
                    type="intolerance" if not health_profile.has_celiac else "allergy",
                    severity=severity,
                    message="Contains gluten" + (" - CELIAC ALERT!" if health_profile.has_celiac else ""),
                    icon="🚨" if health_profile.has_celiac else "⚠️"
                ))
        
        # Check custom intolerances
        for intolerance in health_profile.intolerances:
            if self._contains_allergen(food.name, intolerance):
                warnings.append(schemas.HealthWarning(
                    type="intolerance",
                    severity="warning",
                    message=f"May contain {intolerance}",
                    icon="⚠️"
                ))
        
        # Check diabetes
        if health_profile.has_diabetes:
            if food.carbs > self.CONDITION_TRIGGERS["diabetes"]["high_carbs"]:
                warnings.append(schemas.HealthWarning(
                    type="health_condition",
                    severity="warning",
                    message=f"High carbs ({actual_carbs:.1f}g) - Monitor blood sugar",
                    icon="🩺"
                ))
        
        # Check high cholesterol
        if health_profile.has_high_cholesterol:
            if food.fats > self.CONDITION_TRIGGERS["high_cholesterol"]["high_total_fat"]:
                warnings.append(schemas.HealthWarning(
                    type="health_condition",
                    severity="warning",
                    message=f"High fat ({actual_fats:.1f}g) - May affect cholesterol",
                    icon="🩺"
                ))
        
        # Check heart disease
        if health_profile.has_heart_disease:
            if food.fats > self.CONDITION_TRIGGERS["heart_disease"]["high_total_fat"]:
                warnings.append(schemas.HealthWarning(
                    type="health_condition",
                    severity="warning",
                    message=f"High fat ({actual_fats:.1f}g) - Heart health concern",
                    icon="❤️"
                ))
        
        # Check kidney disease
        if health_profile.has_kidney_disease:
            if food.protein > self.CONDITION_TRIGGERS["kidney_disease"]["high_protein"]:
                warnings.append(schemas.HealthWarning(
                    type="health_condition",
                    severity="warning",
                    message=f"High protein ({actual_protein:.1f}g) - Kidney concern",
                    icon="🩺"
                ))
        
        # Check dietary restrictions
        for restriction in health_profile.dietary_restrictions:
            if self._violates_dietary_restriction(food.name, restriction):
                warnings.append(schemas.HealthWarning(
                    type="dietary",
                    severity="info",
                    message=f"Not {restriction}",
                    icon="ℹ️"
                ))
        
        return warnings
    
    def _contains_allergen(self, food_name: str, allergen: str) -> bool:
        """Check if food name contains allergen keywords"""
        food_lower = food_name.lower()
        allergen_lower = allergen.lower()
        
        # Check direct match
        if allergen_lower in food_lower:
            return True
        
        # Check keyword list
        if allergen_lower in self.ALLERGEN_KEYWORDS:
            keywords = self.ALLERGEN_KEYWORDS[allergen_lower]
            return any(keyword in food_lower for keyword in keywords)
        
        return False
    
    def _violates_dietary_restriction(self, food_name: str, restriction: str) -> bool:
        """Check if food violates dietary restriction"""
        food_lower = food_name.lower()
        restriction_lower = restriction.lower()
        
        # Simple keyword matching (can be enhanced with ML)
        if restriction_lower == "vegetarian":
            meat_keywords = ["chicken", "beef", "pork", "lamb", "fish", "meat", "bacon"]
            return any(keyword in food_lower for keyword in meat_keywords)
        
        elif restriction_lower == "vegan":
            animal_keywords = ["chicken", "beef", "pork", "lamb", "fish", "meat", 
                             "milk", "cheese", "butter", "egg", "honey", "yogurt"]
            return any(keyword in food_lower for keyword in animal_keywords)
        
        elif restriction_lower == "halal":
            haram_keywords = ["pork", "bacon", "ham", "alcohol", "wine", "beer"]
            return any(keyword in food_lower for keyword in haram_keywords)
        
        elif restriction_lower == "kosher":
            non_kosher_keywords = ["pork", "bacon", "ham", "shellfish", "shrimp", "crab"]
            return any(keyword in food_lower for keyword in non_kosher_keywords)
        
        return False

# Global instance
health_checker = HealthChecker()
