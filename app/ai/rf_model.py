"""Random Forest model for food recommendations."""

import joblib
import json
from pathlib import Path


class FoodRecommendationModel:
    """Model for predicting food recommendations."""

    def __init__(self, model_path, scaler_path=None):
        """Initialize the model."""
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path) if scaler_path else None
        self._load_model()

    def _load_model(self):
        """Load the model and scaler."""
        try:
            self.model = joblib.load(self.model_path)
            if self.scaler_path and self.scaler_path.exists():
                self.scaler = joblib.load(self.scaler_path)
            else:
                self.scaler = None

            feature_names_path = self.model_path.parent / "feature_names.json"
            if feature_names_path.exists():
                with open(feature_names_path, 'r') as f:
                    self.feature_names = json.load(f)
            else:
                self.feature_names = ['calories_100g', 'protein_100g', 'carbs_100g', 'fat_100g']

            self._available = True
        except Exception as e:
            print(f"Error loading model: {e}")
            self._available = False

    def is_available(self):
        """Check if the model is available."""
        return self._available

    def _prepare_features(self, nutrition_data):
        """Prepare features for prediction."""
        features = [
            nutrition_data['calories_100g'],
            nutrition_data['protein_100g'],
            nutrition_data['carbs_100g'],
            nutrition_data['fat_100g']
        ]
        if self.scaler:
            features = self.scaler.transform([features])[0]
        return features

    def predict_multiple_with_confidence(self, nutrition_data):
        """Predict recommendations for food with confidence scores."""
        if not self.is_available():
            return []

        try:
            features = self._prepare_features(nutrition_data)
            probabilities = self.model.predict_proba([features])[0]
            prediction = self.model.predict([features])[0]

            # Generate explanation
            high_protein = nutrition_data['protein_100g'] > 15
            low_fat = nutrition_data['fat_100g'] < 10
            balanced = (nutrition_data['protein_100g'] / nutrition_data['calories_100g']) > 0.1

            explanation = []
            if high_protein:
                explanation.append("high in protein")
            if low_fat:
                explanation.append("low in fat")
            if balanced:
                explanation.append("has balanced macronutrients")

            explanation_text = "This food is " + ", ".join(explanation) if explanation else "This food has average nutritional values"

            return [{
                "recommended": bool(prediction),
                "confidence": float(max(probabilities)),
                "explanation": explanation_text
            }]
        except Exception as e:
            print(f"Error predicting: {e}")
            return []