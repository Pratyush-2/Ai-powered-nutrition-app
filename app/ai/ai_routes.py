from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.schemas import FactOut
from app.ai.retriever import retrieve_facts
from app.ai_pipeline.random_forest import classify_food
from app.ai_pipeline.llm_integration import get_llm_explanation, chat_with_llm
from app.crud import get_user_profile
from app.database import get_db
from sqlalchemy.orm import Session
from app.services.food_search import search_food_by_name

router = APIRouter(prefix="/ai", tags=["AI"])

ACTIVITY_LEVEL_MAPPING = {
    "low": 1,
    "medium": 2,
    "high": 3,
}

@router.get("/get-nutrition-facts/", response_model=List[FactOut])
def get_nutrition_facts(q: str, k: int = 3):
    results = retrieve_facts(query=q, k=k)
    # results already have keys: score, fact, meta
    return results

@router.post("/classify-food/")
def classify_food_endpoint(food_name: str, user_id: int, db: Session = Depends(get_db)):
    user_profile = get_user_profile(db, user_id=user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")

    food_data = search_food_by_name(food_name)
    if not food_data or not food_data.get("products"):
        raise HTTPException(status_code=404, detail="Food not found")

    product = food_data["products"][0]
    nutriments = product.get("nutriments", {})

    food_features = {
        "calories": nutriments.get("energy-kcal_100g", 0),
        "protein": nutriments.get("proteins_100g", 0),
        "fat": nutriments.get("fat_100g", 0),
        "sugar": nutriments.get("sugars_100g", 0),
        "carbohydrates": nutriments.get("carbohydrates_100g", 0),
    }

    user_features = {
        "age": user_profile.age,
        "bmi": user_profile.weight_kg / ((user_profile.height_cm / 100) ** 2),
        "activity_level": ACTIVITY_LEVEL_MAPPING.get(user_profile.activity_level.lower(), 1),
    }

    classification = classify_food(food_features, user_features)
    return classification

@router.post("/generate-explanation/")
def generate_explanation_endpoint(classification: Dict[str, Any], rag_output: str):
    explanation = get_llm_explanation(classification, rag_output)
    return {"explanation": explanation}

from app.schemas import FactOut, ChatRequest

@router.post("/chat/")
def chat_endpoint(request: ChatRequest):
    response = chat_with_llm(request.user_query, request.user_history)
    return {"response": response}
