from typing import List, Dict, Any
from . import models, schemas

class HealthChecker:
    """Service to check food safety based on user's health profile"""
    
    # Common allergen keywords
    ALLERGEN_KEYWORDS = {
        "peanuts": ["peanut", "groundnut"],
        "tree_nuts": ["almond", "cashew", "walnut", "pistachio", "hazelnut", "pecan", "macadamia", "brazil nut", "pinenut"],
        "dairy": [
            "milk", "cheese", "butter", "cream", "yogurt", "whey", "casein", "lactose", 
            "ghee", "curd", "paneer", "kefir", "buttermilk", "nougat", "ice cream", "gelato",
            "lactalbumin", "lactoglobulin", "milk solids", "milk fat", "sodium caseinate"
        ],
        "eggs": ["egg", "albumin", "mayonnaise", "meringue", "surimi"],
        "soy": ["soy", "tofu", "edamame", "tempeh", "miso", "natto", "shoyu", "tamari", "lecithin"],
        "wheat": ["wheat", "flour", "bread", "pasta", "semolina", "couscous", "bulgur", "seitan", "farina"],
        "gluten": ["wheat", "barley", "rye", "gluten", "malt", "brewer's yeast", "spelt", "kamut", "triticale"],
        "shellfish": ["shrimp", "crab", "lobster", "prawn", "crayfish", "krill", "clam", "mussel", "oyster", "scallop", "squid", "octopus", "calamari"],
        "fish": ["fish", "salmon", "tuna", "cod", "halibut", "tilapia", "trout", "anchovy", "sardine"],
        "sesame": ["sesame", "tahini", "gomasio", "halvah"],
    }
    
    # Hidden Sugars for Diabetes Check
    HIDDEN_SUGARS = [
        "sugar", "glucose", "fructose", "sucrose", "maltose", "dextrose", "lactose", "galactose",
        "syrup", "corn syrup", "agave", "honey", "molasses", "nectar", "cane", "caramel",
        "maltodextrin", "dextrin", "diastatic malt", "barley malt", "turbinado", "muscovado",
        "treacle", "demerara", "panela", "juice concentrate", "ethyl maltol"
    ]

    # Health condition nutritional triggers (per 100g)
    CONDITION_TRIGGERS = {
        "diabetes": {
            "high_sugar": 15,  # g per 100g
            "high_carbs": 45,  # g per 100g (Lowered from 50)
            "spike_risk_ratio": 10.0, # Carbs/Protein ratio. If > 10, high spike risk
        },
        "high_cholesterol": {
            "high_saturated_fat": 5,  # g per 100g
            "high_total_fat": 20,  # g per 100g
        },
        "hypertension": {
            "high_sodium": 400,  # mg per 100g
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
        for allergy in (health_profile.allergies or []):
            if self._contains_allergen(ingredients_lower, allergy):
                warnings.append(schemas.HealthWarning(
                    type="allergy",
                    severity="critical",
                    message=f"⚠️ ALLERGY ALERT: Ingredients contain {allergy}!",
                    icon="🚨"
                ))
        
        # Check lactose intolerance
        if health_profile.lactose_intolerant:
            # Skip if explicitly lactose-free
            if "lactose-free" in ingredients_lower or "lactose free" in ingredients_lower:
                pass  # Product is lactose-free, no warning needed
            else:
                # Comprehensive dairy keyword list
                dairy_keywords = [
                    "milk", "cream", "cheese", "butter", "whey", "lactose", "casein",
                    "yogurt", "yoghurt", "curd", "paneer", "ghee", "kefir", "buttermilk",
                    "ice cream", "gelato", "milk powder", "milk solids", "milk fat",
                    "lactalbumin", "lactoglobulin", "sodium caseinate", "nougat"
                ]
                if any(keyword in ingredients_lower for keyword in dairy_keywords):
                    warnings.append(schemas.HealthWarning(
                        type="intolerance",
                        severity="warning",
                        message="Contains dairy/lactose - May cause digestive discomfort",
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
        for intolerance in (health_profile.intolerances or []):
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
        for allergy in (health_profile.allergies or []):
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
        for intolerance in (health_profile.intolerances or []):
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
        
        # Calculate actual sodium if available
        multiplier = actual_carbs / food.carbs if food.carbs > 0 else 1.0
        actual_sodium = (food.sodium or 0) * multiplier
        
        # Check diabetes
        if health_profile.has_diabetes:
            # 1. Carb Check
            if food.carbs > self.CONDITION_TRIGGERS["diabetes"]["high_carbs"]:
                severity = "danger" if food.carbs > 60 else "warning"
                warnings.append(schemas.HealthWarning(
                    type="health_condition",
                    severity=severity,
                    message=f"⚠️ High carbs ({actual_carbs:.1f}g) - Test blood sugar 2 hours after eating",
                    icon="🩺"
                ))
            
            # 2. Refined Carb Detection (High Glycemic Index Risk)
            if food.ingredients_text:
                refined_carb_keywords = [
                    "white flour", "refined flour", "white rice", "white bread",
                    "corn syrup", "maltodextrin", "refined sugar", "white sugar"
                ]
                found_refined = [k for k in refined_carb_keywords if k in food.ingredients_text.lower()]
                if found_refined and food.carbs > 30:
                    warnings.append(schemas.HealthWarning(
                        type="health_condition",
                        severity="warning",
                        message=f"⚠️ Contains refined carbs - May spike blood sugar quickly",
                        icon="📈"
                    ))
            
            # 3. Hidden Sugar Check
            if food.ingredients_text:
                found_sugars = [s for s in self.HIDDEN_SUGARS if s in food.ingredients_text.lower()]
                if found_sugars:
                    # Limit to top 3 for brevity
                    found_str = ", ".join(found_sugars[:3])
                    warnings.append(schemas.HealthWarning(
                        type="health_condition",
                        severity="warning",
                        message=f"⚠️ Contains added sugars ({found_str})",
                        icon="🍬"
                    ))
            
            # 4. Spike Risk (Carb/Protein Ratio)
            # High carbs with low protein/fat causes faster spikes
            if actual_carbs > 30:
                # Add small epsilon to avoid division by zero
                protein_fat_sum = actual_protein + actual_fats + 0.1
                ratio = actual_carbs / protein_fat_sum
                if ratio > self.CONDITION_TRIGGERS["diabetes"].get("spike_risk_ratio", 10.0):
                    warnings.append(schemas.HealthWarning(
                        type="health_condition",
                        severity="warning",
                        message=f"⚠️ High Spike Risk: Unbalanced carbs ({ratio:.1f}x protein/fat)",
                        icon="📈"
                    ))
        
        # Check hypertension (high blood pressure)
        if health_profile.has_hypertension:
            if food.sodium and food.sodium > 400:  # High sodium threshold (mg per 100g)
                severity = "danger" if food.sodium > 800 else "warning"
                warnings.append(schemas.HealthWarning(
                    type="health_condition",
                    severity=severity,
                    message=f"⚠️ High sodium ({actual_sodium:.0f}mg) - May raise blood pressure",
                    icon="🧂"
                ))
        
        # Check high cholesterol
        if health_profile.has_high_cholesterol:
            if food.fats > self.CONDITION_TRIGGERS["high_cholesterol"]["high_total_fat"]:
                severity = "danger" if food.fats > 20 else "warning"
                warnings.append(schemas.HealthWarning(
                    type="health_condition",
                    severity=severity,
                    message=f"⚠️ High fat ({actual_fats:.1f}g) - May affect cholesterol levels",
                    icon="🩺"
                ))
            
            # Check for saturated fat indicators in ingredients
            if food.ingredients_text and any(bad_fat in food.ingredients_text.lower() 
                                            for bad_fat in ['palm oil', 'coconut oil', 'butter', 'cream', 'lard']):
                warnings.append(schemas.HealthWarning(
                    type="health_condition",
                    severity="warning",
                    message="⚠️ Contains saturated fats - May increase LDL cholesterol",
                    icon="🧈"
                ))
        
        # Check heart disease
        if health_profile.has_heart_disease:
            if food.fats > self.CONDITION_TRIGGERS["heart_disease"]["high_total_fat"]:
                warnings.append(schemas.HealthWarning(
                    type="health_condition",
                    severity="danger",
                    message=f"⚠️ High fat ({actual_fats:.1f}g) - Heart health concern",
                    icon="❤️"
                ))
            
            # Sodium is also critical for heart disease
            if food.sodium and food.sodium > 400:
                warnings.append(schemas.HealthWarning(
                    type="health_condition",
                    severity="danger",
                    message=f"⚠️ High sodium ({actual_sodium:.0f}mg) - Strains cardiovascular system",
                    icon="❤️"
                ))
        
        # Check kidney disease
        if health_profile.has_kidney_disease:
            if food.protein > self.CONDITION_TRIGGERS["kidney_disease"]["high_protein"]:
                warnings.append(schemas.HealthWarning(
                    type="health_condition",
                    severity="warning",
                    message=f"⚠️ High protein ({actual_protein:.1f}g) - May strain kidneys",
                    icon="🩺"
                ))
            
            # Sodium is critical for kidney disease
            if food.sodium and food.sodium > 300:
                warnings.append(schemas.HealthWarning(
                    type="health_condition",
                    severity="danger",
                    message=f"⚠️ High sodium ({actual_sodium:.0f}mg) - Kidney concern",
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
        
        for restriction in (health_profile.dietary_restrictions or []):
            if self._violates_dietary_restriction(food_name, restriction):
                warnings.append(schemas.HealthWarning(
                    type="dietary",
                    severity="info",
                    message=f"Not {restriction}",
                    icon="ℹ️"
                ))
        
        return warnings
    
    # False positive handling
    EXCEPTIONS = {
        "butter": ["peanut", "almond", "cashew", "soya", "soy", "fruit", "cocoa", "shea", "cookie", "apple", "pumpkin", "body"],
        "milk": ["coconut", "almond", "soy", "soya", "oat", "rice", "cashew", "hemp", "magnesia", "muscle", "tiger"],
        "cream": ["coconut", "shaving", "face", "hand", "sun", "tartar", "body"],
        "egg": ["eggplant"],
        "cheese": ["headcheese"],  # rare but valid
        "nut": ["donut", "doughnut", "coconut", "butternut", "chestnut", "nutmeg"], 
        "fish": ["starfish", "jellyfish", "silverfish", "crayfish", "shellfish"], 
    }

    def _contains_allergen(self, text: str, allergen: str) -> bool:
        """Check if text contains allergen with smart exclusion logic"""
        text_lower = text.lower()
        allergen_lower = allergen.lower()
        
        # Get list of keywords to check
        keywords = [allergen_lower]
        if allergen_lower in self.ALLERGEN_KEYWORDS:
            keywords.extend(self.ALLERGEN_KEYWORDS[allergen_lower])
            
        for keyword in keywords:
            if self._is_smart_match(text_lower, keyword):
                return True
                
        return False

    def _is_smart_match(self, text: str, keyword: str) -> bool:
        """
        Check if keyword exists in text as a whole word, 
        AND is not part of an excluded phrase (e.g. 'peanut butter')
        """
        import re
        
        # 1. Word Boundary Check (prevents 'pineapple' matching 'apple')
        # \b matches word boundary
        if not re.search(r'\b' + re.escape(keyword) + r'\b', text):
            return False

        # 2. Check Exceptions (Negative Context)
        if keyword in self.EXCEPTIONS:
            for exc in self.EXCEPTIONS[keyword]:
                # Matches: "peanut butter", "peanut-butter", "peanut  butter"
                # But ensures we don't match "butter peanut" (which would be weird but implies butter)
                # We check if the EXCEPTION word immediately precedes the KEYWORD
                
                # Regex: \b(exception)[\s-]*(keyword)\b
                pattern = r'\b' + re.escape(exc) + r'[\s-]*' + re.escape(keyword) + r'\b'
                if re.search(pattern, text):
                    # Found an exclusion phrase (e.g. "coconut milk")
                    # But wait! What if text is "milk, coconut milk"?
                    # The simple search found "milk". The exclusion found "coconut milk".
                    # Does "milk" exist outside of "coconut milk"?
                    
                    # Remove the independent exclusion phrases and check again!
                    cleaned_text = re.sub(pattern, '', text)
                    
                    # If keyword still exists in cleaned text, it's a real match
                    if re.search(r'\b' + re.escape(keyword) + r'\b', cleaned_text):
                        return True
                    else:
                        return False # Only existed as part of exception
                        
        return True
    
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
