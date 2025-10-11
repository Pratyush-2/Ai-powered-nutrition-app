"""
AI routes and orchestration for the nutrition API.

This module provides the main AI endpoints that orchestrate the complete
pipeline: data fetching, RF classification, retrieval, verification, and LLM generation.
"""

import time
import logging
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .fetch_openfoodfacts import OpenFoodFactsFetcher
from .retriever import retrieve_facts
from .rf_model import predict_food_recommendation
from .llm_service import generate_explanation, chat_message
from .verifier import verify_macro_claims
from .security import rate_limit, input_validator, add_security_headers
from app import crud, models
from backend.ai import llm_service
fetcher = OpenFoodFactsFetcher()

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/ai", tags=["AI"])

# Pydantic models for API
class FactOut(BaseModel):
    score: float
    fact: str
    meta: dict

class FoodClassificationRequest(BaseModel):
    user_id: int
    food_name: str
    quantity_g: float

class FoodClassificationResponse(BaseModel):
    recommended: bool
    confidence: float
    explanation: str
    raw_nutrition: dict

class ExplanationRequest(BaseModel):
    user_id: int
    food_name: str
    quantity_g: float = 100.0
    extra_context: str = ""

class ExplanationResponse(BaseModel):
    recommendation: bool
    confidence: float
    explanation: str
    evidence: List[FactOut]
    verifier_status: str
    timings: dict

class ChatRequest(BaseModel):
    user_id: int
    message: str
    food_context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    timings: dict

from app.database import get_db

@router.get("/get-nutrition-facts/", response_model=List[FactOut])
@rate_limit(max_requests=30, window_seconds=60)
async def get_nutrition_facts_endpoint(q: str, k: int = 3, request: Request = None):
    """
    Retrieve nutrition facts using semantic search.
    
    Args:
        q: Search query
        k: Number of results to return
        
    Returns:
        List of nutrition facts with scores and metadata
    """
    start_time = time.time()
    
    try:
        # Validate inputs
        q = input_validator.validate_query(q)
        k = max(1, min(k, 10))  # Limit k to 1-10
        
        # Retrieve facts
        facts = retrieve_facts(q, k)
        
        # Format response
        response = []
        for fact in facts:
            response.append(FactOut(
                score=fact["score"],
                fact=fact["fact_text"],
                meta=fact["meta"]
            ))
        
        logger.info(f"Retrieved {len(response)} facts for query: {q}")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving facts: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving facts: {str(e)}")

@router.post("/classify-food/", response_model=FoodClassificationResponse)
@rate_limit(max_requests=20, window_seconds=60)
async def classify_food_endpoint(request: FoodClassificationRequest, db: Session = Depends(get_db)):
    """
    Classify food recommendation using Random Forest model.
    
    Args:
        request: Food classification request
        db: Database session
        
    Returns:
        Classification result with confidence and explanation
    """
    start_time = time.time()
    
    try:
        # Validate inputs
        request.user_id = input_validator.validate_user_id(request.user_id)
        request.food_name = input_validator.validate_food_name(request.food_name)
        request.quantity_g = input_validator.validate_quantity(request.quantity_g)
        
        # Get food data
        food_data = fetcher.get_food_data(request.food_name)
        if not food_data:
            raise HTTPException(status_code=404, detail=f"Food data not found for: {request.food_name}")
        
        # Scale nutrition to requested quantity
        scale_factor = request.quantity_g / 100.0
        scaled_nutrition = {
            "calories_100g": food_data["calories_100g"] * scale_factor,
            "protein_100g": food_data["protein_100g"] * scale_factor,
            "carbs_100g": food_data["carbs_100g"] * scale_factor,
            "fat_100g": food_data["fat_100g"] * scale_factor
        }
        
        # Get prediction
        recommended, confidence, explanation = predict_food_recommendation(scaled_nutrition)
        
        # Prepare raw nutrition data
        raw_nutrition = {
            "name": food_data["name"],
            "calories_per_100g": food_data["calories_100g"],
            "protein_per_100g": food_data["protein_100g"],
            "carbs_per_100g": food_data["carbs_100g"],
            "fat_per_100g": food_data["fat_100g"],
            "calories_for_quantity": scaled_nutrition["calories_100g"],
            "protein_for_quantity": scaled_nutrition["protein_100g"],
            "carbs_for_quantity": scaled_nutrition["carbs_100g"],
            "fat_for_quantity": scaled_nutrition["fat_100g"],
            "quantity_g": request.quantity_g
        }
        
        return FoodClassificationResponse(
            recommended=recommended,
            confidence=confidence,
            explanation=explanation,
            raw_nutrition=raw_nutrition
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error classifying food: {e}")
        raise HTTPException(status_code=500, detail=f"Error classifying food: {str(e)}")

@router.post("/generate-explanation/", response_model=ExplanationResponse)
@rate_limit(max_requests=10, window_seconds=60)
async def generate_explanation_endpoint(request: ExplanationRequest, db: Session = Depends(get_db)):
    """
    Generate comprehensive explanation using the full AI pipeline.
    
    Args:
        request: Explanation request
        db: Database session
        
    Returns:
        Complete explanation with evidence and verification
    """
    start_time = time.time()
    timings = {}
    
    try:
        # Validate inputs
        request.user_id = input_validator.validate_user_id(request.user_id)
        request.food_name = input_validator.validate_food_name(request.food_name)
        request.quantity_g = input_validator.validate_quantity(request.quantity_g)
        if request.extra_context:
            request.extra_context = input_validator.validate_message(request.extra_context)
        
        # Step 1: Load user profile
        profile_start = time.time()
        # This would load from database in real implementation
        user_profile = {
            "age": 30,  # Placeholder
            "gender": "Unknown",
            "weight_kg": 70,
            "height_cm": 170,
            "activity_level": "Moderate",
            "goal": "General Health"
        }
        timings["load_profile"] = time.time() - profile_start
        
        # Step 2: Get food data
        food_start = time.time()
        food_data = fetcher.get_food_data(request.food_name)
        if not food_data:
            raise HTTPException(status_code=404, detail=f"Food data not found for: {request.food_name}")
        timings["fetch_food_data"] = time.time() - food_start
        
        # Step 3: RF classification
        rf_start = time.time()
        scale_factor = request.quantity_g / 100.0
        scaled_nutrition = {
            "calories_100g": food_data["calories_100g"] * scale_factor,
            "protein_100g": food_data["protein_100g"] * scale_factor,
            "carbs_100g": food_data["carbs_100g"] * scale_factor,
            "fat_100g": food_data["fat_100g"] * scale_factor
        }
        recommended, confidence, rf_explanation = predict_food_recommendation(scaled_nutrition)
        rf_result = {
            "recommended": recommended,
            "confidence": confidence,
            "explanation": rf_explanation
        }
        timings["rf_classification"] = time.time() - rf_start
        
        # Step 4: Retrieve facts
        retrieval_start = time.time()
        retrieved_facts = retrieve_facts(request.food_name, k=3)
        timings["retrieve_facts"] = time.time() - retrieval_start
        
        # Step 5: Pre-verification (optional)
        verification_start = time.time()
        verifier_status = "skipped"
        if retrieved_facts:
            # Simple verification check
            suggested_portions = {request.food_name: request.quantity_g}
            verification_result = verify_macro_claims("", retrieved_facts, suggested_portions)
            verifier_status = verification_result["status"]
        timings["verification"] = time.time() - verification_start
        
        # Step 6: LLM generation
        llm_start = time.time()
        explanation = generate_explanation(
            user_profile, 
            rf_result, 
            retrieved_facts, 
            request.extra_context
        )
        timings["llm_generation"] = time.time() - llm_start
        
        # Format evidence
        evidence = []
        for fact in retrieved_facts:
            evidence.append(FactOut(
                score=fact["score"],
                fact=fact["fact_text"],
                meta=fact["meta"]
            ))
        
        timings["total"] = time.time() - start_time
        
        return ExplanationResponse(
            recommendation=recommended,
            confidence=confidence,
            explanation=explanation,
            evidence=evidence,
            verifier_status=verifier_status,
            timings=timings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating explanation: {str(e)}")

@router.post("/chat/", response_model=ChatResponse)
@rate_limit(max_requests=15, window_seconds=60)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Chatbot endpoint with local fallback and context-aware responses."""
    # Load user profile
    user_profile = crud.get_user_profile(db, request.user_id)
    # Retrieve recent meal logs for context
    recent_logs = crud.get_logs_by_user(db, request.user_id, limit=5)
    # Call chat_message with recent_logs for local fallback
    start_time = time.time()
    timings = {}
    response = llm_service.chat_message(user_profile, request.message, recent_logs=recent_logs)
    timings["llm_generation"] = time.time() - start_time
    return ChatResponse(response=response, timings=timings)
    start_time = time.time()
    timings = {}
    
    try:
        # Validate inputs
        request.user_id = input_validator.validate_user_id(request.user_id)
        request.message = input_validator.validate_message(request.message)
        if request.food_context:
            request.food_context = input_validator.validate_message(request.food_context)
        
        # Load user profile
        profile_start = time.time()
        user_profile = {
            "age": 30,  # Placeholder
            "gender": "Unknown", 
            "weight_kg": 70,
            "height_cm": 170,
            "activity_level": "Moderate",
            "goal": "General Health"
        }
        timings["load_profile"] = time.time() - profile_start
        
        # Generate response
        llm_start = time.time()
        response = chat_message(user_profile, request.message)
        timings["llm_generation"] = time.time() - llm_start
        
        timings["total"] = time.time() - start_time
        
        return ChatResponse(
            response=response,
            timings=timings
        )
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

@router.get("/health/")
async def health_check():
    """Health check endpoint for AI services."""
    try:
        # Check if services are available
        from .retriever import get_retriever
        from .rf_model import get_model
        from backend.ai.llm_service import get_llm_service
        
        retriever = get_retriever()
        model = get_model()
        llm = get_llm_service()
        
        status = {
            "retriever": retriever.is_available(),
            "rf_model": model.is_available(),
            "llm_service": llm.is_available(),
            "overall": retriever.is_available() and model.is_available()
        }
        
        return {
            "status": "healthy" if status["overall"] else "degraded",
            "services": status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

@router.post("/train/")
async def train_random_forest_endpoint(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Retrain the Random Forest model using latest meal logs and user feedback from the database.
    This runs in the background and updates the model file (random_forest_model.pkl).
    """
    try:
        # Import trainer
        from backend.ai.train_rf import FoodRecommendationTrainer
        import os
        # Fetch all meal logs from DB
        logs = db.query(models.DailyLog).all()
        # Convert logs to training data format
        X, y = [], []
        for log in logs:
            if log.food:
                X.append([
                    log.food.calories,
                    log.food.protein,
                    log.food.carbs,
                    log.food.fats
                ])
                # For now, use quantity > threshold as positive label (customize as needed)
                y.append(1 if log.quantity > 50 else 0)
        # Run training in background
        def retrain_rf():
            trainer = FoodRecommendationTrainer(model_path="models/random_forest_model.pkl")
            trainer.train(X, y)
        background_tasks.add_task(retrain_rf)
        return {"status": "training started", "num_samples": len(X)}
    except Exception as e:
        logger.error(f"Error retraining RF model: {e}")
        raise HTTPException(status_code=500, detail=f"Error retraining RF model: {str(e)}")
