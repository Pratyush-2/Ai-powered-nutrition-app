from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas

def get_health_profile(db: Session, user_id: int) -> Optional[models.UserHealthProfile]:
    """Get user's health profile"""
    return db.query(models.UserHealthProfile).filter(
        models.UserHealthProfile.user_id == user_id
    ).first()

def create_health_profile(
    db: Session, 
    health_profile: schemas.UserHealthProfileCreate, 
    user_id: int
) -> models.UserHealthProfile:
    """Create a new health profile for user"""
    db_health_profile = models.UserHealthProfile(
        user_id=user_id,
        **health_profile.dict()
    )
    db.add(db_health_profile)
    db.commit()
    db.refresh(db_health_profile)
    return db_health_profile

def update_health_profile(
    db: Session,
    user_id: int,
    health_profile: schemas.UserHealthProfileUpdate
) -> Optional[models.UserHealthProfile]:
    """Update user's health profile"""
    db_health_profile = get_health_profile(db, user_id)
    
    if not db_health_profile:
        return None
    
    # Update only provided fields
    update_data = health_profile.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_health_profile, field, value)
    
    db.commit()
    db.refresh(db_health_profile)
    return db_health_profile

def get_or_create_health_profile(
    db: Session,
    user_id: int
) -> models.UserHealthProfile:
    """Get health profile or create empty one if doesn't exist"""
    health_profile = get_health_profile(db, user_id)
    
    if not health_profile:
        # Create empty health profile
        health_profile = models.UserHealthProfile(user_id=user_id)
        db.add(health_profile)
        db.commit()
        db.refresh(health_profile)
    
    return health_profile
