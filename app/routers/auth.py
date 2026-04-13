from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas, auth, models
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.UserProfile)
def register(user: schemas.UserProfileCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    try:
        return crud.create_user_profile(db=db, profile=user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )



@router.post("/login", response_model=schemas.Token)
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.email},
    )
    return {"access_token": access_token, "token_type": "bearer"}

from pydantic import BaseModel

class MockOAuthRequest(BaseModel):
    email: str
    name: str

@router.post("/mock-oauth", response_model=schemas.Token)
def mock_oauth(request: MockOAuthRequest, db: Session = Depends(get_db)):
    """Simulate OAuth login flow, auto-registering if they don't exist."""
    user = crud.get_user_by_email(db, email=request.email)
    
    if not user:
        # Auto construct a profile for the OAuth user
        mock_profile = schemas.UserProfileCreate(
            email=request.email,
            password="OAUTH_MOCK_PASSWORD_DO_NOT_USE",
            name=request.name,
            age=25,
            weight_kg=70.0,
            height_cm=170.0,
            gender="Not Specified",
            activity_level="moderately_active",
            goal="maintain"
        )
        user = crud.create_user_profile(db=db, profile=mock_profile)
        
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

