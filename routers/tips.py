from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from database import SessionLocal
from models import RelationshipTip, User, UserProfile
from auth import get_current_user
from datetime import datetime
import random

router = APIRouter(prefix="/tips", tags=["Relationship Tips"])


@router.get("/")
async def get_tips(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get relationship tips"""
    # Check if user has premium
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    has_premium = user_profile and user_profile.premium_until and user_profile.premium_until > datetime.utcnow()
    
    query = db.query(RelationshipTip)
    
    if category:
        query = query.filter(RelationshipTip.category == category)
    
    if not has_premium:
        query = query.filter(RelationshipTip.premium == False)
    
    tips = query.all()
    return {
        "tips": [
            {
                "id": t.id,
                "title": t.title,
                "content": t.content,
                "category": t.category,
                "premium": t.premium
            }
            for t in tips
        ]
    }

@router.get("/random")
async def get_random_tip(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a random relationship tip"""
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    has_premium = user_profile and user_profile.premium_until and user_profile.premium_until > datetime.utcnow()
    
    query = db.query(RelationshipTip)
    
    if category:
        query = query.filter(RelationshipTip.category == category)
    
    if not has_premium:
        query = query.filter(RelationshipTip.premium == False)
    
    tips = query.all()
    if not tips:
        raise HTTPException(status_code=404, detail="No tips available")
    
    tip = random.choice(tips)
    return {
        "id": tip.id,
        "title": tip.title,
        "content": tip.content,
        "category": tip.category,
        "premium": tip.premium
    }

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all tip categories"""
    categories = db.query(RelationshipTip.category).distinct().all()
    return {"categories": [c[0] for c in categories if c[0]]}

@router.get("/{tip_id}")
async def get_tip(
    tip_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific tip"""
    tip = db.query(RelationshipTip).filter(RelationshipTip.id == tip_id).first()
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    
    # Check premium access
    if tip.premium:
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        has_premium = user_profile and user_profile.premium_until and user_profile.premium_until > datetime.utcnow()
        if not has_premium:
            raise HTTPException(status_code=403, detail="Premium subscription required")
    
    return {
        "id": tip.id,
        "title": tip.title,
        "content": tip.content,
        "category": tip.category,
        "premium": tip.premium
    }
