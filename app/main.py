import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("sys.path on startup:", sys.path)
print("sys.executable on startup:", sys.executable)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn.access")

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import crud, schemas, models, auth
from .database import get_db, engine, Base
from app.routers import auth as auth_router
from app.ai.ai_routes import router as ai_router
from app.services.food_search import search_food_by_name
from app import health_crud
from app.health_checker import health_checker
from typing import List, Optional

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nutrition API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router.router)
app.include_router(ai_router)

# User Profile
@app.get("/profiles/me", response_model=schemas.UserProfile)
def read_users_me(current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    return current_user

# Food
@app.post("/foods/", response_model=schemas.Food)
def create_food(food: schemas.FoodCreate, db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    return crud.create_food(db=db, food=food)

@app.get("/foods/", response_model=List[schemas.Food])
def read_foods(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    return crud.get_foods(db=db, skip=skip, limit=limit)

# Daily Logs
@app.post("/logs/", response_model=schemas.DailyLog)
def create_log(log: schemas.DailyLogCreate, db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    return crud.create_daily_log(db=db, log=log, user_id=current_user.id)

@app.get("/logs/", response_model=List[schemas.DailyLog])
def read_logs(log_date: Optional[str] = None, db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    if log_date:
        return crud.get_logs_by_date_and_user(db=db, user_id=current_user.id, date=log_date)
    return crud.get_logs_by_user(db=db, user_id=current_user.id)

@app.put("/logs/{log_id}", response_model=schemas.DailyLog)
def update_log(log_id: int, log_update: schemas.DailyLogUpdate, db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    # TODO: Add check to ensure user can only update their own logs
    return crud.update_daily_log(db=db, log_id=log_id, log_update=log_update)

@app.delete("/logs/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    # TODO: Add check to ensure user can only delete their own logs
    return crud.delete_daily_log(db, log_id=log_id)

# Totals
@app.get("/totals/{log_date}", response_model=schemas.DailyTotals)
def get_daily_totals(log_date: str, db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    totals = crud.get_daily_totals_by_user(db, current_user.id, log_date)
    return schemas.DailyTotals(date=log_date, **totals)

# Goals
@app.post("/goals/", response_model=schemas.UserGoal)
def set_goal(goal: schemas.UserGoalCreate, db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    return crud.set_goal(db=db, goal=goal, user_id=current_user.id)

@app.get("/goals/", response_model=List[schemas.UserGoal])
def get_user_goals(db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    return crud.get_user_goals(db=db, user_id=current_user.id)

@app.put("/goals/{goal_id}", response_model=schemas.UserGoal)
def update_goal_endpoint(goal_id: int, goal: schemas.UserGoalUpdate, db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    return crud.update_goal(db=db, goal_id=goal_id, goal=goal)

# Food Search
@app.get("/search-food/{food_name}")
def search_food(food_name: str, current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    """Search for food using OpenFoodFacts API and local database"""
    try:
        result = search_food_by_name(food_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Food search failed: {str(e)}")

# Health Profile
@app.get("/health-profile/", response_model=schemas.UserHealthProfile)
def get_health_profile(db: Session = Depends(get_db), current_user: models.UserProfile = Depends(auth.get_current_active_user)):
    """Get user's health profile"""
    health_profile = health_crud.get_or_create_health_profile(db, current_user.id)
    return health_profile

@app.post("/health-profile/", response_model=schemas.UserHealthProfile)
def create_health_profile_endpoint(
    health_profile: schemas.UserHealthProfileCreate,
    db: Session = Depends(get_db),
    current_user: models.UserProfile = Depends(auth.get_current_active_user)
):
    """Create or update user's health profile"""
    existing = health_crud.get_health_profile(db, current_user.id)
    
    if existing:
        # Update existing
        return health_crud.update_health_profile(db, current_user.id, schemas.UserHealthProfileUpdate(**health_profile.dict()))
    else:
        # Create new
        return health_crud.create_health_profile(db, health_profile, current_user.id)

@app.put("/health-profile/", response_model=schemas.UserHealthProfile)
def update_health_profile_endpoint(
    health_profile: schemas.UserHealthProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.UserProfile = Depends(auth.get_current_active_user)
):
    """Update user's health profile"""
    updated = health_crud.update_health_profile(db, current_user.id, health_profile)
    if not updated:
        raise HTTPException(status_code=404, detail="Health profile not found")
    return updated

# Food Safety Check
@app.post("/check-food-safety/", response_model=List[schemas.HealthWarning])
def check_food_safety(
    food_id: int,
    quantity: float = 100.0,
    db: Session = Depends(get_db),
    current_user: models.UserProfile = Depends(auth.get_current_active_user)
):
    """Check if a food is safe for the user based on their health profile"""
    # Get food
    food = crud.get_food(db, food_id)
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    
    # Get health profile
    health_profile = health_crud.get_or_create_health_profile(db, current_user.id)
    
    # Check safety
    warnings = health_checker.check_food_safety(food, health_profile, quantity)
    
    return warnings
