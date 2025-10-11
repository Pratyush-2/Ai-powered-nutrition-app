"""
Random Forest runtime model for food recommendations.

This module provides the runtime interface for the trained Random Forest model,
including prediction, confidence scoring, and explanation generation.
"""

import json
import numpy as np
import joblib
from pathlib import Path
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class FoodRecommendationModel:
    """Runtime interface for the trained Random Forest model."""
    
    def __init__(self, model_path: str = "models/random_forest_model.pkl",
                 scaler_path: str = "models/scaler.pkl"):
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.metadata = None
        
        self._load_model()
    
    def _load_model(self):
        """Load the trained model, scaler, and metadata."""
        try:
            if not self.model_path.exists():
                logger.warning(f"Model not found at {self.model_path}")
                self.model = None
                self.scaler = None
                return
            
            if not self.scaler_path.exists():
                logger.warning(f"Scaler not found at {self.scaler_path}")
                self.model = None
                self.scaler = None
                return
            
            # Load model and scaler
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            
            # Load feature names
            feature_names_path = self.model_path.parent / "feature_names.json"
            if feature_names_path.exists():
                with open(feature_names_path, 'r') as f:
                    self.feature_names = json.load(f)
            
            # Load metadata
            metadata_path = self.model_path.parent / "model_metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
            
            logger.info("Food recommendation model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
            self.scaler = None
    
    def is_available(self) -> bool:
        """Check if the model is loaded and ready to use."""
        return self.model is not None and self.scaler is not None
    
    def prepare_features(self, nutrition_data: Dict) -> np.ndarray:
        """
        Prepare feature vector from nutrition data.
        
        Args:
            nutrition_data: Dictionary with nutrition information
                Expected keys: calories_100g, protein_100g, carbs_100g, fat_100g
            
        Returns:
            Feature vector ready for prediction
        """
        # Extract basic nutrition values
        calories = nutrition_data.get("calories_100g", 0)
        protein = nutrition_data.get("protein_100g", 0)
        carbs = nutrition_data.get("carbs_100g", 0)
        fat = nutrition_data.get("fat_100g", 0)
        
        # Calculate derived features
        total_calories = calories
        if total_calories > 0:
            protein_ratio = (protein * 4) / total_calories  # 4 cal/g protein
            carb_ratio = (carbs * 4) / total_calories  # 4 cal/g carbs
            fat_ratio = (fat * 9) / total_calories  # 9 cal/g fat
            protein_density = protein / (total_calories / 100)  # g protein per 100 cal
        else:
            protein_ratio = 0
            carb_ratio = 0
            fat_ratio = 0
            protein_density = 0
        
        # Macronutrient balance (how close to ideal ratios)
        ideal_protein = 0.25
        ideal_carbs = 0.45
        ideal_fat = 0.30
        macro_balance = 1 - abs(protein_ratio - ideal_protein) - abs(carb_ratio - ideal_carbs) - abs(fat_ratio - ideal_fat)
        
        # Create feature vector in the same order as training
        features = np.array([
            calories,
            protein,
            carbs,
            fat,
            protein_ratio,
            carb_ratio,
            fat_ratio,
            protein_density,
            macro_balance
        ])
        
        return features.reshape(1, -1)
    
    def predict_with_confidence(self, nutrition_data: Dict) -> Tuple[bool, float, str]:
        """
        Predict food recommendation with confidence and explanation.
        
        Args:
            nutrition_data: Dictionary with nutrition information
            
        Returns:
            Tuple of (recommended: bool, confidence: float, explanation: str)
        """
        if not self.is_available():
            return False, 0.0, "Model not available"
        
        try:
            # Prepare features
            features = self.prepare_features(nutrition_data)
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get prediction and probability
            prediction = self.model.predict(features_scaled)[0]
            probabilities = self.model.predict_proba(features_scaled)[0]
            
            # Calculate confidence
            confidence = float(max(probabilities))
            recommended = bool(prediction)
            
            # Generate explanation
            explanation = self._generate_explanation(nutrition_data, recommended, confidence)
            
            return recommended, confidence, explanation
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            return False, 0.0, f"Prediction error: {str(e)}"
    
    def _generate_explanation(self, nutrition_data: Dict, recommended: bool, 
                            confidence: float) -> str:
        """Generate human-readable explanation for the prediction."""
        calories = nutrition_data.get("calories_100g", 0)
        protein = nutrition_data.get("protein_100g", 0)
        carbs = nutrition_data.get("carbs_100g", 0)
        fat = nutrition_data.get("fat_100g", 0)
        
        # Base explanation
        if recommended:
            base = f"Recommended (confidence: {confidence:.1%}). "
        else:
            base = f"Not recommended (confidence: {confidence:.1%}). "
        
        # Add specific reasoning
        reasons = []
        
        # Calorie analysis
        if calories < 200:
            reasons.append("low calorie content")
        elif calories > 400:
            reasons.append("high calorie content")
        
        # Protein analysis
        if protein > 15:
            reasons.append("high protein content")
        elif protein < 5:
            reasons.append("low protein content")
        
        # Macronutrient balance
        total_calories = calories
        if total_calories > 0:
            protein_ratio = (protein * 4) / total_calories
            fat_ratio = (fat * 9) / total_calories
            
            if protein_ratio > 0.2 and fat_ratio < 0.4:
                reasons.append("good macronutrient balance")
            elif protein_ratio < 0.1:
                reasons.append("poor protein content")
            elif fat_ratio > 0.5:
                reasons.append("high fat content")
        
        # Combine reasons
        if reasons:
            if recommended:
                base += f"Key factors: {', '.join(reasons)}."
            else:
                base += f"Concerns: {', '.join(reasons)}."
        else:
            base += "Nutritional profile is moderate."
        
        return base.strip()
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from the trained model."""
        if not self.is_available():
            return {}
        
        if self.feature_names is None:
            return {}
        
        importance = dict(zip(self.feature_names, self.model.feature_importances_))
        return importance
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        if not self.is_available():
            return {"status": "not_loaded"}
        
        info = {
            "status": "loaded",
            "model_path": str(self.model_path),
            "scaler_path": str(self.scaler_path),
            "feature_names": self.feature_names,
            "n_features": len(self.feature_names) if self.feature_names else 0
        }
        
        if self.metadata:
            info.update({
                "model_type": self.metadata.get("model_type"),
                "n_estimators": self.metadata.get("n_estimators"),
                "max_depth": self.metadata.get("max_depth"),
                "trained_at": self.metadata.get("trained_at")
            })
        
        return info
    
    def predict_batch(self, nutrition_data_list: list) -> list:
        """
        Predict recommendations for multiple food items.
        
        Args:
            nutrition_data_list: List of nutrition data dictionaries
            
        Returns:
            List of prediction results
        """
        if not self.is_available():
            return [{"error": "Model not available"} for _ in nutrition_data_list]
        
        results = []
        for nutrition_data in nutrition_data_list:
            recommended, confidence, explanation = self.predict_with_confidence(nutrition_data)
            results.append({
                "recommended": recommended,
                "confidence": confidence,
                "explanation": explanation
            })
        
        return results


# Global model instance
_model_instance = None

def get_model() -> FoodRecommendationModel:
    """Get the global model instance."""
    global _model_instance
    if _model_instance is None:
        _model_instance = FoodRecommendationModel()
    return _model_instance

def predict_food_recommendation(nutrition_data: Dict) -> Tuple[bool, float, str]:
    """
    Convenience function to predict food recommendation.
    
    Args:
        nutrition_data: Dictionary with nutrition information
        
    Returns:
        Tuple of (recommended, confidence, explanation)
    """
    model = get_model()
    return model.predict_with_confidence(nutrition_data)

