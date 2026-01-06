from datetime import date, datetime
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

# ---------- User Health Profile ----------
class UserHealthProfileBase(BaseModel):
    # Health Conditions
    has_diabetes: bool = False
    diabetes_type: Optional[str] = None
    has_high_cholesterol: bool = False
    has_hypertension: bool = False
    has_heart_disease: bool = False
    has_kidney_disease: bool = False
    has_celiac: bool = False
    
    # Food Intolerances
    lactose_intolerant: bool = False
    gluten_intolerant: bool = False
    
    # Custom lists
    allergies: List[str] = []
    intolerances: List[str] = []
    dietary_restrictions: List[str] = []
    avoid_ingredients: List[str] = []

class UserHealthProfileCreate(UserHealthProfileBase):
    pass

class UserHealthProfileUpdate(BaseModel):
    has_diabetes: Optional[bool] = None
    diabetes_type: Optional[str] = None
    has_high_cholesterol: Optional[bool] = None
    has_hypertension: Optional[bool] = None
    has_heart_disease: Optional[bool] = None
    has_kidney_disease: Optional[bool] = None
    has_celiac: Optional[bool] = None
    lactose_intolerant: Optional[bool] = None
    gluten_intolerant: Optional[bool] = None
    allergies: Optional[List[str]] = None
    intolerances: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    avoid_ingredients: Optional[List[str]] = None

class UserHealthProfile(UserHealthProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ---------- Health Warning ----------
class HealthWarning(BaseModel):
    type: str  # "allergy", "intolerance", "health_condition", "dietary"
    severity: str  # "critical", "warning", "info"
    message: str
    icon: str

# ---------- Food Safety Check Request ----------
class FoodSafetyCheckRequest(BaseModel):
    food_id: int
    quantity: float = 100.0
