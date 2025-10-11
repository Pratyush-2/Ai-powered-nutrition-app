from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import crud, schemas, utils
from .database import get_db, engine, Base
from .user_profiles import router as profiles_router
from backend.ai.ai_routes import router as ai_router

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nutrition API")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(profiles_router)
app.include_router(ai_router)

# Food endpoints
@app.post("/foods/", response_model=schemas.Food)
def create_food(food: schemas.FoodCreate, db: Session = Depends(get_db)):
    return crud.create_food(db=db, food=food)

@app.get("/foods/", response_model=list[schemas.Food])
def read_foods(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_foods(db=db, skip=skip, limit=limit)

# Daily Logs
@app.post("/logs/", response_model=schemas.DailyLog)
def create_log(log: schemas.DailyLogCreate, db: Session = Depends(get_db)):
    return crud.create_daily_log(db=db, log=log)

@app.get("/logs/{log_date}", response_model=list[schemas.DailyLog])
def read_logs(log_date: str, db: Session = Depends(get_db)):
    return crud.get_logs_by_date(db=db, date=log_date)

# Totals
@app.get("/totals/{log_date}", response_model=schemas.DailyTotals)
def get_daily_totals(log_date: str, db: Session = Depends(get_db)):
    totals = utils.calculate_goals(db, log_date)
    return schemas.DailyTotals(date=log_date, **totals)

# Goals
@app.post("/goals/", response_model=schemas.UserGoal)
def set_goal(goal: schemas.UserGoalCreate, db: Session = Depends(get_db)):
    return crud.set_goal(db=db, goal=goal)

@app.get("/goals/", response_model=list[schemas.UserGoal])
def get_goals(db: Session = Depends(get_db)):
    return crud.get_goals(db=db)
