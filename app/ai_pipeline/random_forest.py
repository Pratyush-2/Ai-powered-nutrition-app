
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

def train_model():
    # This is a placeholder for training data
    # In a real application, this would come from a database or a CSV file
    data = {
        'calories': [200, 500, 100, 800, 300],
        'protein': [10, 25, 5, 40, 15],
        'fat': [5, 20, 2, 30, 10],
        'sugar': [10, 40, 5, 50, 15],
        'carbohydrates': [30, 60, 15, 100, 40],
        'age': [25, 45, 30, 50, 35],
        'bmi': [22, 28, 24, 30, 26],
        'activity_level': [1, 2, 1, 3, 2], # 1: low, 2: medium, 3: high
        'recommended': [1, 0, 1, 0, 1] # 1: yes, 0: no
    }
    df = pd.DataFrame(data)

    X = df.drop('recommended', axis=1)
    y = df['recommended']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Ensure the directory exists
    os.makedirs(os.path.dirname('models/rf_model.joblib'), exist_ok=True)
    
    joblib.dump(model, 'models/rf_model.joblib')
    joblib.dump(scaler, 'models/scaler.joblib')

def classify_food(food_features, user_features):
    model = joblib.load('models/rf_model.joblib')
    scaler = joblib.load('models/scaler.joblib')

    features = {**food_features, **user_features}
    df = pd.DataFrame([features])

    # Ensure the order of columns is the same as during training
    df = df[['calories', 'protein', 'fat', 'sugar', 'carbohydrates', 'age', 'bmi', 'activity_level']]

    scaled_features = scaler.transform(df)
    
    prediction = model.predict(scaled_features)
    probability = model.predict_proba(scaled_features)

    return {
        "recommended": bool(prediction[0]),
        "confidence": float(max(probability[0]))
    }

if __name__ == '__main__':
    train_model()
