"""
Random Forest training for food recommendation.

This module handles training a Random Forest classifier to predict
whether a food item is recommended based on nutrition features.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FoodRecommendationTrainer:
    """Trains Random Forest model for food recommendations."""
    
    def __init__(self, model_path: str = "models/random_forest_model.pkl", 
                 scaler_path: str = "models/scaler.pkl"):
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path)
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Model parameters
        self.n_estimators = 200
        self.max_depth = 12
        self.random_state = 42
        
        self.model = None
        self.scaler = None
        self.feature_names = None
    
    def generate_synthetic_labels(self, facts: List[Dict], 
                                rules: Dict = None) -> List[Dict]:
        """
        Generate synthetic training labels using heuristic rules.
        
        Args:
            facts: List of nutrition fact dictionaries
            rules: Custom labeling rules (optional)
            
        Returns:
            List of facts with added 'recommended' labels
        """
        if rules is None:
            rules = {
                "max_calories": 300,
                "min_protein": 8,
                "healthy_categories": ["Vegetable", "Fruit", "Legume", "Nuts", "Seeds"],
                "unhealthy_categories": ["Snack", "Dessert", "Fast Food"],
                "max_fat_ratio": 0.4,  # Max 40% calories from fat
                "min_protein_ratio": 0.15  # Min 15% calories from protein
            }
        
        labeled_facts = []
        
        for fact in facts:
            # Extract features
            calories = fact.get("calories_100g", 0)
            protein = fact.get("protein_100g", 0)
            carbs = fact.get("carbs_100g", 0)
            fat = fact.get("fat_100g", 0)
            name = fact.get("name", "").lower()
            
            # Calculate ratios
            total_calories = calories
            if total_calories > 0:
                protein_ratio = (protein * 4) / total_calories  # 4 cal/g protein
                fat_ratio = (fat * 9) / total_calories  # 9 cal/g fat
            else:
                protein_ratio = 0
                fat_ratio = 0
            
            # Apply labeling rules
            recommended = 0  # Default to not recommended
            
            # Rule 1: Low calorie, high protein
            if calories <= rules["max_calories"] and protein >= rules["min_protein"]:
                recommended = 1
            
            # Rule 2: Healthy categories
            for category in rules["healthy_categories"]:
                if category.lower() in name:
                    recommended = 1
                    break
            
            # Rule 3: Good macronutrient ratios
            if protein_ratio >= rules["min_protein_ratio"] and fat_ratio <= rules["max_fat_ratio"]:
                recommended = 1
            
            # Rule 4: Unhealthy categories override
            for category in rules["unhealthy_categories"]:
                if category.lower() in name:
                    recommended = 0
                    break
            
            # Rule 5: Very high calorie foods
            if calories > 500:
                recommended = 0
            
            # Add label to fact
            labeled_fact = fact.copy()
            labeled_fact["recommended"] = recommended
            labeled_facts.append(labeled_fact)
        
        # Save labeling rules for future reference
        rules_path = self.model_path.parent / "label_rules.json"
        with open(rules_path, 'w') as f:
            json.dump(rules, f, indent=2)
        
        logger.info(f"Generated labels for {len(labeled_facts)} facts using heuristic rules")
        return labeled_facts
    
    def prepare_features(self, facts: List[Dict]) -> Tuple[np.ndarray, List[str]]:
        """
        Prepare feature matrix from nutrition facts.
        
        Args:
            facts: List of labeled nutrition facts
            
        Returns:
            Tuple of (feature_matrix, feature_names)
        """
        feature_data = []
        
        for fact in facts:
            # Basic nutrition features
            calories = fact.get("calories_100g", 0)
            protein = fact.get("protein_100g", 0)
            carbs = fact.get("carbs_100g", 0)
            fat = fact.get("fat_100g", 0)
            
            # Calculate derived features
            total_calories = calories
            if total_calories > 0:
                protein_ratio = (protein * 4) / total_calories
                carb_ratio = (carbs * 4) / total_calories
                fat_ratio = (fat * 9) / total_calories
                protein_density = protein / (total_calories / 100)  # g protein per 100 cal
            else:
                protein_ratio = 0
                carb_ratio = 0
                fat_ratio = 0
                protein_density = 0
            
            # Macronutrient balance
            macro_balance = 1 - abs(protein_ratio - 0.25) - abs(carb_ratio - 0.45) - abs(fat_ratio - 0.30)
            
            # Create feature vector
            features = [
                calories,
                protein,
                carbs,
                fat,
                protein_ratio,
                carb_ratio,
                fat_ratio,
                protein_density,
                macro_balance
            ]
            
            feature_data.append(features)
        
        feature_names = [
            "calories_100g",
            "protein_100g", 
            "carbs_100g",
            "fat_100g",
            "protein_ratio",
            "carb_ratio",
            "fat_ratio",
            "protein_density",
            "macro_balance"
        ]
        
        return np.array(feature_data), feature_names
    
    def train(self, facts: List[Dict], test_size: float = 0.2) -> Dict:
        """
        Train the Random Forest model.
        
        Args:
            facts: List of labeled nutrition facts
            test_size: Fraction of data to use for testing
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Training Random Forest with {len(facts)} samples...")
        
        # Prepare features and labels
        X, feature_names = self.prepare_features(facts)
        y = np.array([fact["recommended"] for fact in facts])
        
        self.feature_names = feature_names
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.random_state, stratify=y
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Get feature importances
        feature_importance = dict(zip(feature_names, self.model.feature_importances_))
        
        # Generate classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        
        metrics = {
            "accuracy": accuracy,
            "feature_importance": feature_importance,
            "classification_report": report,
            "n_samples": len(facts),
            "n_train": len(X_train),
            "n_test": len(X_test),
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth
        }
        
        logger.info(f"Training completed. Accuracy: {accuracy:.3f}")
        return metrics
    
    def save_model(self):
        """Save the trained model and scaler."""
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained yet")
        
        # Save model
        joblib.dump(self.model, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
        
        # Save scaler
        joblib.dump(self.scaler, self.scaler_path)
        logger.info(f"Scaler saved to {self.scaler_path}")
        
        # Save feature names
        feature_names_path = self.model_path.parent / "feature_names.json"
        with open(feature_names_path, 'w') as f:
            json.dump(self.feature_names, f, indent=2)
        
        # Save model metadata
        metadata = {
            "model_type": "RandomForestClassifier",
            "n_estimators": self.n_estimators,
            "max_depth": self.max_depth,
            "random_state": self.random_state,
            "feature_names": self.feature_names,
            "trained_at": datetime.now().isoformat()
        }
        
        metadata_path = self.model_path.parent / "model_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def load_model(self):
        """Load the trained model and scaler."""
        if not self.model_path.exists() or not self.scaler_path.exists():
            raise FileNotFoundError("Model files not found")
        
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        
        # Load feature names
        feature_names_path = self.model_path.parent / "feature_names.json"
        with open(feature_names_path, 'r') as f:
            self.feature_names = json.load(f)
        
        logger.info("Model loaded successfully")
    
    def explain_prediction(self, features: np.ndarray) -> Dict:
        """
        Explain a single prediction using feature importance and decision path.
        
        Args:
            features: Feature vector for a single sample
            
        Returns:
            Dictionary with explanation details
        """
        if self.model is None:
            raise ValueError("Model not loaded")
        
        # Get prediction and probability
        prediction = self.model.predict([features])[0]
        probability = self.model.predict_proba([features])[0]
        
        # Get feature importance for this prediction
        feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
        
        # Get decision path (simplified)
        decision_path = []
        for i, (name, value) in enumerate(zip(self.feature_names, features)):
            decision_path.append({
                "feature": name,
                "value": float(value),
                "importance": float(feature_importance[name])
            })
        
        # Sort by importance
        decision_path.sort(key=lambda x: x["importance"], reverse=True)
        
        return {
            "prediction": int(prediction),
            "probability": float(probability[1]),  # Probability of being recommended
            "confidence": float(max(probability)),
            "feature_importance": feature_importance,
            "decision_path": decision_path[:5],  # Top 5 most important features
            "explanation": self._generate_text_explanation(prediction, probability, decision_path[:3])
        }
    
    def _generate_text_explanation(self, prediction: int, probability: np.ndarray, 
                                 top_features: List[Dict]) -> str:
        """Generate human-readable explanation for prediction."""
        confidence = max(probability)
        
        if prediction == 1:
            base = f"This food is recommended (confidence: {confidence:.1%}). "
        else:
            base = f"This food is not recommended (confidence: {confidence:.1%}). "
        
        # Add feature-based explanation
        if top_features:
            top_feature = top_features[0]
            feature_name = top_feature["feature"].replace("_", " ").title()
            value = top_feature["value"]
            
            if "calories" in top_feature["feature"]:
                if value < 200:
                    base += f"Low calorie content ({value:.0f} cal/100g) makes it suitable. "
                else:
                    base += f"High calorie content ({value:.0f} cal/100g) is a concern. "
            elif "protein" in top_feature["feature"]:
                if value > 10:
                    base += f"High protein content ({value:.1f}g/100g) is beneficial. "
                else:
                    base += f"Low protein content ({value:.1f}g/100g) is limiting. "
            elif "ratio" in top_feature["feature"]:
                if value > 0.2:
                    base += f"Good macronutrient balance ({value:.1%}) supports recommendation. "
                else:
                    base += f"Poor macronutrient balance ({value:.1%}) affects recommendation. "
        
        return base.strip()


def main():
    """CLI interface for training the Random Forest model."""
    import argparse
    from .fetch_openfoodfacts import OpenFoodFactsFetcher
    
    parser = argparse.ArgumentParser(description="Train Random Forest model for food recommendations")
    parser.add_argument("--jsonl", type=str, default="data/nutrition_facts.jsonl", 
                       help="Path to JSONL file with nutrition facts")
    parser.add_argument("--model-path", type=str, default="models/random_forest_model.pkl",
                       help="Path to save the trained model")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set size")
    parser.add_argument("--seed-db", action="store_true", help="Seed database before training")
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Seed database if requested
    if args.seed_db:
        logger.info("Seeding database with common foods...")
        fetcher = OpenFoodFactsFetcher()
        common_foods = ["paneer", "apple", "banana", "spinach", "almonds", 
                       "white rice", "chicken breast", "dal", "yogurt", "oats"]
        fetcher.seed_database(common_foods)
    
    # Load training data
    trainer = FoodRecommendationTrainer(model_path=args.model_path)
    
    if Path(args.jsonl).exists():
        # Load from JSONL
        facts = []
        with open(args.jsonl, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    facts.append(json.loads(line))
    else:
        logger.error(f"JSONL file not found: {args.jsonl}")
        return
    
    # Generate labels
    labeled_facts = trainer.generate_synthetic_labels(facts)
    
    # Train model
    metrics = trainer.train(labeled_facts, test_size=args.test_size)
    
    # Save model
    trainer.save_model()
    
    # Print results
    print(f"\nTraining completed!")
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"Training samples: {metrics['n_train']}")
    print(f"Test samples: {metrics['n_test']}")
    print(f"\nTop 5 most important features:")
    for feature, importance in sorted(metrics['feature_importance'].items(), 
                                    key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {feature}: {importance:.3f}")


if __name__ == "__main__":
    main()

