"""Random Forest model trainer for food recommendations."""

import joblib
import json
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


class FoodRecommendationTrainer:
    """Trainer for the food recommendation Random Forest model."""

    def __init__(self, model_path, scaler_path=None):
        """Initialize the trainer."""
        self.model_path = Path(model_path)
        self.scaler_path = Path(scaler_path) if scaler_path else None
        self.feature_names = ['calories_100g', 'protein_100g', 'carbs_100g', 'fat_100g']
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()

    def _extract_features(self, data):
        """Extract features from the data."""
        X = []
        y = []
        for item in data:
            features = [
                item['calories_100g'],
                item['protein_100g'],
                item['carbs_100g'],
                item['fat_100g']
            ]
            X.append(features)
            y.append(item['recommended'])
        return X, y

    def train(self, data, test_size=0.2):
        """Train the model and return metrics."""
        X, y = self._extract_features(data)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        self.model.fit(X_train_scaled, y_train)

        # Get metrics
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)

        return {
            "accuracy": test_score,
            "train_score": train_score,
            "n_train": len(X_train),
            "n_test": len(X_test)
        }

    def save_model(self):
        """Save the trained model and scaler."""
        # Create directories if they don't exist
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        if self.scaler_path:
            self.scaler_path.parent.mkdir(parents=True, exist_ok=True)

        # Save model
        joblib.dump(self.model, self.model_path)

        # Save scaler if path provided
        if self.scaler_path:
            joblib.dump(self.scaler, self.scaler_path)

        # Save feature names
        feature_names_path = self.model_path.parent / "feature_names.json"
        with open(feature_names_path, 'w') as f:
            json.dump(self.feature_names, f)