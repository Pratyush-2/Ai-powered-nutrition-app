from datetime import date
from typing import Optional
from pydantic import BaseModel

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
        from_attributes = True  # Pydantic v2 replacement for orm_mode

# ---------- Daily Logs ----------
class DailyLogBase(BaseModel):
    date: date
    quantity: int
    food_id: int

class DailyLogCreate(DailyLogBase):
    pass

class DailyLog(DailyLogBase):
    id: int
    food: Food | None = None

    class Config:
        from_attributes = True

# ---------- Totals ----------
class DailyTotals(BaseModel):
    date: date
    calories: float
    protein: float
    carbs: float
    fats: float

# ---------- Goals ----------  # 🔹 CHANGES: Use *_goal to match DB columns
class UserGoalBase(BaseModel):
    calories_goal: float
    protein_goal: float
    carbs_goal: float
    fats_goal: float

class UserGoalCreate(UserGoalBase):
    pass

class UserGoal(UserGoalBase):
    id: int

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
    pass

class UserProfile(UserProfileBase):
    id: int

    class Config:
        from_attributes = True

class UserProfileResponse(UserProfileBase):
    id: int

    class Config:
        from_attributes = True
