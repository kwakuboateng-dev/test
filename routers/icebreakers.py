from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import SessionLocal
from models import IcebreakerPrompt, UserIcebreaker, User, UserProfile
from auth import get_current_user
from datetime import datetime
import random

router = APIRouter(prefix="/icebreakers", tags=["Icebreakers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/random")
async def get_random_icebreaker(
    category: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a random icebreaker prompt"""
    # Check if user has premium
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    has_premium = user_profile and user_profile.premium_until and user_profile.premium_until > datetime.utcnow()
    
    query = db.query(IcebreakerPrompt)
    
    # Filter by category if provided
    if category:
        query = query.filter(IcebreakerPrompt.category == category)
    
    # Filter premium prompts if user doesn't have premium
    if not has_premium:
        query = query.filter(IcebreakerPrompt.premium == False)
    
    prompts = query.all()
    if not prompts:
        raise HTTPException(status_code=404, detail="No icebreakers available")
    
    prompt = random.choice(prompts)
    return {"id": prompt.id, "text": prompt.text, "category": prompt.category, "premium": prompt.premium}

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all available icebreaker categories"""
    categories = db.query(IcebreakerPrompt.category).distinct().all()
    return {"categories": [c[0] for c in categories if c[0]]}

@router.post("/{prompt_id}/use")
async def mark_prompt_used(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark an icebreaker as used by the current user"""
    prompt = db.query(IcebreakerPrompt).filter(IcebreakerPrompt.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Icebreaker not found")
    
    user_icebreaker = UserIcebreaker(user_id=current_user.id, prompt_id=prompt_id)
    db.add(user_icebreaker)
    db.commit()
    
    return {"message": "Icebreaker marked as used"}

@router.get("/my/history")
async def get_user_icebreaker_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's icebreaker usage history"""
    history = db.query(UserIcebreaker).filter(UserIcebreaker.user_id == current_user.id).order_by(UserIcebreaker.used_at.desc()).limit(20).all()
    return {"history": [{"prompt_id": h.prompt_id, "used_at": h.used_at.isoformat()} for h in history]}
