from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List, Dict, Any
from app.schemas import FactOut, ChatRequest, ClassifyRequest, NutritionResult
from app.ai.retriever import retrieve_facts
from app.ai_pipeline.nutrition_engine import classify_food
from app.ai_pipeline.llm_integration import get_llm_explanation
from app.ai_pipeline.enhanced_image_recognition import identify_food_from_image
from app.ai_pipeline.barcode_scanner import scan_barcode_from_image
from app.ai_pipeline.sugar_analysis import analyze_sugar_composition
from app.crud import get_user_profile, get_user_goals
from app.database import get_db
from sqlalchemy.orm import Session
from app.services.food_search import search_food_by_name
import logging
from app.ai_pipeline.enhanced_image_recognition import food_recognizer
import os
from app import auth, models

router = APIRouter(prefix="/ai", tags=["AI"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ACTIVITY_LEVEL_MAPPING = {
    "low": 1,
    "medium": 2,
    "high": 3,
}

@router.get("/get-nutrition-facts/", response_model=List[FactOut])
def get_nutrition_facts(q: str, k: int = 3, current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    results = retrieve_facts(query=q, k=k)
    return results

@router.post("/classify/")
def classify_food_endpoint(request: ClassifyRequest, db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    try:
        user_profile = current_user
        user_goals = get_user_goals(db, user_id=user_profile.id)

        nutrition_db = getattr(food_recognizer, 'nutrition_database', None) or getattr(food_recognizer, 'nutrition_db', None)
        
        food_data = search_food_by_name(request.food_name)
        
        if not food_data or not food_data.get("products"):
            normalized_key = _normalize_food_name(request.food_name)
            if nutrition_db and normalized_key in nutrition_db:
                nutrition = nutrition_db[normalized_key]
                food_data = {
                    "products": [{"nutriments": {"energy-kcal_100g": nutrition["calories"], "proteins_100g": nutrition["protein"], "fat_100g": nutrition["fat"], "sugars_100g": nutrition["sugar"], "carbohydrates_100g": nutrition["carbs"], "fiber_100g": nutrition["fiber"]}}]
                }
            else:
                raise HTTPException(status_code=404, detail="Food not found")
        
        product = food_data["products"][0]
        nutriments = product.get("nutriments", {})

        food_features = {
            "food_name": request.food_name, 
            "calories": nutriments.get("energy-kcal_100g", 0), 
            "protein": nutriments.get("proteins_100g", 0), 
            "fat": nutriments.get("fat_100g", 0), 
            "sugar": nutriments.get("sugars_100g", 0), 
            "carbohydrates": nutriments.get("carbohydrates_100g", 0),
            "fiber": nutriments.get("fiber_100g", 0)
        }
        
        user_features = {"age": user_profile.age, "bmi": user_profile.weight_kg / ((user_profile.height_cm / 100) ** 2), "activity_level": ACTIVITY_LEVEL_MAPPING.get(user_profile.activity_level.lower(), 1)}

        classification = classify_food(food_features, user_features, user_goals)
        
        response = {"recommendation": "recommended" if classification["recommended"] else "not recommended", "health_score": classification["score"], "confidence": classification["confidence"], "explanation": classification["reasoning"], "nutritional_breakdown": classification["nutritional_breakdown"], "nutritional_details": classification["nutritional_details"]}
        
        return response
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@router.post("/chat/")
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    from app.ai.llm_integration import chat_with_ai
    response = await chat_with_ai(db, current_user.id, request.query, request.context)
    return {"response": response}

@router.post("/identify-food/")
async def identify_food(file: UploadFile = File(...), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    from app.ai_pipeline.enhanced_image_recognition import IntegratedFoodRecognizer
    fresh_recognizer = IntegratedFoodRecognizer()
    result = fresh_recognizer.identify_food_from_image(file)
    return result

# ... other endpoints can be protected similarly

@router.post("/scan-barcode/")
async def scan_barcode(file: UploadFile = File(...)):
    """Scan barcode from image and lookup nutritional information"""
    try:
        result = scan_barcode_from_image(file)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-sugar/")
def analyze_sugar(food_name: str, total_sugar: float, nutritional_data: Dict = None):
    """Analyze sugar composition (natural vs. added sugars)"""
    try:
        result = analyze_sugar_composition(food_name, total_sugar, nutritional_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/nutrition-analysis/")
def comprehensive_nutrition_analysis(request: ClassifyRequest, db: Session = Depends(get_db)):
    """Complete nutrition analysis including sugar differentiation"""
    try:
        # Get basic classification (existing logic)
        classification = classify_food_endpoint(request, db)
        
        # Add sugar analysis if sugar data is available
        if "nutritional_details" in classification and "sugar_g" in classification["nutritional_details"]:
            sugar_analysis = analyze_sugar_composition(
                request.food_name,
                classification["nutritional_details"]["sugar_g"],
                classification["nutritional_details"]
            )
            classification["sugar_analysis"] = sugar_analysis
            
            # Enhance reasoning with sugar insights
            if sugar_analysis["dominant_type"] == "added" and sugar_analysis["added_sugar_g"] > 10:
                classification["reasoning"] += f" High added sugar content ({sugar_analysis['added_sugar_g']}g/100g) is concerning."
            elif sugar_analysis["dominant_type"] == "natural":
                classification["reasoning"] += f" Sugars are primarily natural ({sugar_analysis['natural_sugar_g']}g/100g)."
        
        return classification
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/test-google-vision/")
def test_google_vision_status():
    """Test if Google Vision API is properly configured"""
    from app.ai_pipeline.enhanced_image_recognition import GOOGLE_VISION_AVAILABLE, food_recognizer
    
    return {
        "google_vision_available": GOOGLE_VISION_AVAILABLE,
        "vision_client_initialized": food_recognizer.vision_client is not None,
        "credentials_file_exists": os.path.exists("analog-reef-470415-q6-b8ddae1e11b3.json")
    }

def _normalize_food_name(food_name: str) -> str:
    """
    Normalize food names for better database matching
    """
    name = food_name.lower().strip()
    
    # Remove common qualifiers and get base food
    qualifiers_to_remove = [
        'breast', 'thigh', 'wing', 'leg', 'drumstick', 'ground', 'minced',
        'fillet', 'steak', 'chop', 'roast', 'cooked', 'raw', 'fresh',
        'frozen', 'canned', 'dried', 'whole', 'skinless', 'boneless'
    ]
    
    words = name.split()
    # Keep only the main food words, remove qualifiers
    filtered_words = [word for word in words if word not in qualifiers_to_remove]
    
    if filtered_words:
        base_name = ' '.join(filtered_words)
    else:
        base_name = words[0] if words else name
    
    # Convert spaces to underscores for database key
    return base_name.replace(' ', '_')
