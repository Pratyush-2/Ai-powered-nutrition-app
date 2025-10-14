from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Dict, Any
from app.schemas import FactOut, ChatRequest, ClassifyRequest
from app.ai.retriever import retrieve_facts
from app.ai_pipeline.random_forest import classify_food
from app.ai_pipeline.llm_integration import get_llm_explanation, chat_with_llm
from app.ai_pipeline.image_recognition import identify_food_from_image
from app.crud import get_user_profile, get_user_goals
from app.database import get_db
from sqlalchemy.orm import Session
from app.services.food_search import search_food_by_name
import logging

router = APIRouter(prefix="/ai", tags=["AI"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@router.post("/classify/")
def classify_food_endpoint(request: ClassifyRequest, db: Session = Depends(get_db)):
    print(f"DEBUG: Starting classification for user {request.user_id}, food {request.food_name}")
    
    user_profile = get_user_profile(db, user_id=request.user_id)
    print(f"DEBUG: User profile retrieved: {user_profile is not None}")
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
    print(f"DEBUG: User profile data: age={user_profile.age}, weight={user_profile.weight_kg}")

    user_goals = get_user_goals(db, user_id=request.user_id)
    print(f"DEBUG: User goals count: {len(user_goals) if user_goals else 0}")
    
    if user_goals:
        first_goal = user_goals[0]
        print(f"DEBUG: First goal values: cal={first_goal.calories_goal}, prot={first_goal.protein_goal}")
        required_goal_attrs = ['calories_goal', 'protein_goal', 'carbs_goal', 'fats_goal']
        for attr in required_goal_attrs:
            if getattr(first_goal, attr) is None:
                print(f"DEBUG: Goal validation failed - {attr} is None")
                raise HTTPException(status_code=400, detail=f"Incomplete user goal data: '{attr}' is missing.")
        print(f"DEBUG: Goal validation passed")

    food_data = search_food_by_name(request.food_name)
    print(f"DEBUG: Food search result: {bool(food_data)}")
    if not food_data or not food_data.get("products"):
        print(f"DEBUG: Food search failed - no products found")
        raise HTTPException(status_code=404, detail="Food not found")
    print(f"DEBUG: Food found: {len(food_data.get('products', []))} products")

    product = food_data["products"][0]
    nutriments = product.get("nutriments", {})
    print(f"DEBUG: Food nutriments: {nutriments}")

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

    print(f"DEBUG: About to call classify_food()")
    classification = classify_food(food_features, user_features, user_goals)
    return classification

@router.post("/generate-explanation/")
def generate_explanation_endpoint(classification: Dict[str, Any], rag_output: str):
    explanation = get_llm_explanation(classification, rag_output)
    return {"explanation": explanation}

@router.post("/chat/")
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """AI chat endpoint with Ollama integration."""
    
    try:
        logger.info(f"Chat request: user {request.user_id}, query '{request.query}'")
        
        # Import here to avoid circular imports
        from app.ai.llm_integration import chat_with_ai
        
        response = chat_with_ai(db, request.user_id, request.query)
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Chat service temporarily unavailable")

@router.post("/identify-food/")
async def identify_food(file: UploadFile = File(...)):
    try:
        food_name = identify_food_from_image(file)
        return {"food_name": food_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
