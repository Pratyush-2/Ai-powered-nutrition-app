from datetime import date
from typing import Optional, List, Any, Dict
from pydantic import BaseModel

# ---------- Token ----------
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# ---------- Food ----------
class FoodBase(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fats: float

class FoodCreate(FoodBase):
    pass

class Food(FoodBase):
    id: int

    class Config:
        from_attributes = True

# ---------- DailyLog ----------
class DailyLogBase(BaseModel):
    quantity: float
    food_id: int

class DailyLogCreate(DailyLogBase):
    date: str

class DailyLogUpdate(BaseModel):
    quantity: Optional[float] = None
    food_id: Optional[int] = None
    date: Optional[str] = None

class DailyLog(DailyLogBase):
    id: int
    date: date
    food: Optional[Food] = None

    class Config:
        from_attributes = True

# ---------- Totals ----------
class DailyTotals(BaseModel):
    date: date
    calories: float
    protein: float
    carbs: float
    fats: float

# ---------- Goals ----------
class UserGoalBase(BaseModel):
    calories_goal: float
    protein_goal: float
    carbs_goal: float
    fats_goal: float

class UserGoalCreate(UserGoalBase):
    pass

class UserGoalUpdate(UserGoalBase):
    pass

class UserGoal(UserGoalBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# ---------- User Profiles ----------
class UserProfileBase(BaseModel):
    name: str
    age: int
    weight_kg: float
    height_cm: float
    gender: str
    activity_level: str
    goal: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    email: str
    password: str

class UserProfile(UserProfileBase):
    id: int
    email: str

    class Config:
        from_attributes = True

class FactOut(BaseModel):
    food_name: str
    recommended: bool
    reason: str

class ChatRequest(BaseModel):
    query: str

class NutritionResult(BaseModel):
    score: float
    recommended: bool
    confidence: float
    reasoning: str
    nutritional_breakdown: Dict[str, float]
    nutritional_details: Dict[str, float]

class ClassifyRequest(BaseModel):
    food_name: str
