from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models, schemas
from .utils import calculate_targets

# ---------- User Profiles ----------
def create_user_profile(db: Session, profile: schemas.UserProfileCreate):
    cals, protein, carbs, fats = calculate_targets(profile)
    db_profile = models.UserProfile(
        name=profile.name,
        age=profile.age,
        weight_kg=profile.weight_kg,
        height_cm=profile.height_cm,
        gender=profile.gender,
        activity_level=profile.activity_level,
        goal=profile.goal,
        target_calories=cals,
        target_protein=protein,
        target_carbs=carbs,
        target_fats=fats
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

def get_user_profile(db: Session, user_id: int):
    profile = db.query(models.UserProfile).filter(models.UserProfile.id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"User profile {user_id} not found")
    return profile

def get_user_profiles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UserProfile).offset(skip).limit(limit).all()

def update_user_profile(db: Session, user_id: int, profile: schemas.UserProfileCreate):
    db_profile = get_user_profile(db, user_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail=f"User profile {user_id} not found")

    for var, value in vars(profile).items():
        setattr(db_profile, var, value) if value else None

    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile

# ---------- Foods ----------
def create_food(db: Session, food: schemas.FoodCreate):
    db_food = models.Food(**food.dict())
    db.add(db_food)
    db.commit()
    db.refresh(db_food)
    return db_food

def get_foods(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Food).offset(skip).limit(limit).all()

def get_food(db: Session, food_id: int):
    return db.query(models.Food).filter(models.Food.id == food_id).first()

def get_food_by_name(db: Session, food_name: str):
    return db.query(models.Food).filter(models.Food.name == food_name).first()

# ---------- Daily Logs ----------
def create_daily_log(db: Session, log: schemas.DailyLogCreate):
    food_id = log.food_id
    if log.food:
        # Check if food exists
        db_food = db.query(models.Food).filter(models.Food.name == log.food.name).first()
        if db_food:
            food_id = db_food.id
        else:
            # Create new food
            new_food = create_food(db, log.food)
            food_id = new_food.id

    if not food_id:
        raise HTTPException(status_code=400, detail="Food not provided")

    db_log = models.DailyLog(
        date=log.date,
        quantity=log.quantity,
        user_id=log.user_id,
        food_id=food_id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_logs_by_date(db: Session, date: str):
    return db.query(models.DailyLog).filter(models.DailyLog.date == date).all()

def get_logs_by_user(db: Session, user_id: int, limit: int = 5):
    """Retrieve the most recent DailyLog entries for a user."""
    return db.query(models.DailyLog).filter(models.DailyLog.user_id == user_id).order_by(models.DailyLog.date.desc()).limit(limit).all()

def get_daily_totals(db: Session, date: str):
    logs = get_logs_by_date(db, date)
    
    totals = {
        "calories": sum(log.food.calories * log.quantity for log in logs if log.food),
        "protein": sum(log.food.protein * log.quantity for log in logs if log.food),
        "carbs": sum(log.food.carbs * log.quantity for log in logs if log.food),
        "fats": sum(log.food.fats * log.quantity for log in logs if log.food),
    }
    
    return totals

# ---------- User Goals ----------
def set_goal(db: Session, goal: schemas.UserGoalCreate):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.id == goal.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User {goal.user_id} not found")
    db_goal = models.UserGoal(**goal.dict())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def get_goals(db: Session, user_id: int):
    db_goals = db.query(models.UserGoal).filter(models.UserGoal.user_id == user_id).all()
    if not db_goals:
        raise HTTPException(status_code=404, detail=f"No goals set for user {user_id}")
    return db_goals
