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
        
        # PRIORITY 1: Check ingredients list (most accurate)
        if food.ingredients_text:
            ingredient_warnings = self._check_ingredients(food.ingredients_text, health_profile)
            warnings.extend(ingredient_warnings)
        
        # PRIORITY 2: Check food name for allergen keywords (fallback)
        else:
            name_warnings = self._check_food_name(food.name, health_profile)
            warnings.extend(name_warnings)
        
        # PRIORITY 3: Check nutritional values for health conditions
        nutrition_warnings = self._check_nutrition(
            food, health_profile, actual_calories, actual_protein, actual_carbs, actual_fats
        )
        warnings.extend(nutrition_warnings)
        
        # PRIORITY 4: Check dietary restrictions
        dietary_warnings = self._check_dietary_restrictions(food.name, health_profile)
        warnings.extend(dietary_warnings)
        
        return warnings
    
    def _check_ingredients(
        self, 
        ingredients_text: str, 
        health_profile: models.UserHealthProfile
    ) -> List[schemas.HealthWarning]:
        """Check ingredient list for allergens and intolerances"""
        warnings = []
        ingredients_lower = ingredients_text.lower()
        
        # Check allergies (CRITICAL)
        for allergy in health_profile.allergies:
            if self._contains_allergen(ingredients_lower, allergy):
                warnings.append(schemas.HealthWarning(
                    type="allergy",
                    severity="critical",
                    message=f"⚠️ ALLERGY ALERT: Ingredients contain {allergy}!",
                    icon="🚨"
                ))
        
        # Check lactose intolerance
        if health_profile.lactose_intolerant:
            dairy_keywords = ["milk", "cream", "cheese", "butter", "whey", "lactose", "casein"]
            if any(keyword in ingredients_lower for keyword in dairy_keywords):
                warnings.append(schemas.HealthWarning(
                    type="intolerance",
                    severity="warning",
                    message="Contains dairy/lactose (found in ingredients)",
                    icon="⚠️"
                ))
        
        # Check gluten intolerance
        if health_profile.gluten_intolerant or health_profile.has_celiac:
            gluten_keywords = ["wheat", "barley", "rye", "gluten", "flour"]
            if any(keyword in ingredients_lower for keyword in gluten_keywords):
                severity = "critical" if health_profile.has_celiac else "warning"
                message = "Contains gluten (found in ingredients)"
                if health_profile.has_celiac:
                    message += " - CELIAC ALERT!"
                warnings.append(schemas.HealthWarning(
                    type="intolerance" if not health_profile.has_celiac else "allergy",
                    severity=severity,
                    message=message,
                    icon="🚨" if health_profile.has_celiac else "⚠️"
                ))
        
        # Check custom intolerances
        for intolerance in health_profile.intolerances:
            if self._contains_allergen(ingredients_lower, intolerance):
                warnings.append(schemas.HealthWarning(
                    type="intolerance",
                    severity="warning",
                    message=f"Ingredients may contain {intolerance}",
                    icon="⚠️"
                ))
        
        return warnings
    
    def _check_food_name(
        self,
        food_name: str,
        health_profile: models.UserHealthProfile
    ) -> List[schemas.HealthWarning]:
        """Fallback: Check food name for allergen keywords"""
        warnings = []
        
        # Check allergies
        for allergy in health_profile.allergies:
            if self._contains_allergen(food_name, allergy):
                warnings.append(schemas.HealthWarning(
                    type="allergy",
                    severity="critical",
                    message=f"⚠️ ALLERGY ALERT: Contains {allergy}!",
                    icon="🚨"
                ))
        
        # Check lactose intolerance
        if health_profile.lactose_intolerant:
            if self._contains_allergen(food_name, "dairy"):
                warnings.append(schemas.HealthWarning(
                    type="intolerance",
                    severity="warning",
                    message="Contains dairy/lactose",
                    icon="⚠️"
                ))
        
        # Check gluten intolerance
        if health_profile.gluten_intolerant or health_profile.has_celiac:
            if self._contains_allergen(food_name, "gluten"):
                severity = "critical" if health_profile.has_celiac else "warning"
                warnings.append(schemas.HealthWarning(
                    type="intolerance" if not health_profile.has_celiac else "allergy",
                    severity=severity,
                    message="Contains gluten" + (" - CELIAC ALERT!" if health_profile.has_celiac else ""),
                    icon="🚨" if health_profile.has_celiac else "⚠️"
                ))
        
        # Check custom intolerances
        for intolerance in health_profile.intolerances:
            if self._contains_allergen(food_name, intolerance):
                warnings.append(schemas.HealthWarning(
                    type="intolerance",
                    severity="warning",
                    message=f"May contain {intolerance}",
                    icon="⚠️"
                ))
        
        return warnings
    
    def _check_nutrition(
        self,
        food: models.Food,
        health_profile: models.UserHealthProfile,
        actual_calories: float,
        actual_protein: float,
        actual_carbs: float,
        actual_fats: float
    ) -> List[schemas.HealthWarning]:
        """Check nutritional values against health conditions"""
        warnings = []
        
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
        
        return warnings
    
    def _check_dietary_restrictions(
        self,
        food_name: str,
        health_profile: models.UserHealthProfile
    ) -> List[schemas.HealthWarning]:
        """Check dietary restrictions"""
        warnings = []
        
        for restriction in health_profile.dietary_restrictions:
            if self._violates_dietary_restriction(food_name, restriction):
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
