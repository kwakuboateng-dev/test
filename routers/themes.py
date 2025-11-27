from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from database import SessionLocal
from models import Theme, UserProfile, User
from auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/themes", tags=["Themes"])

@router.get("/")
async def get_themes(
    premium_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available themes"""
    query = db.query(Theme)
    if premium_only:
        query = query.filter(Theme.premium == True)
    themes = query.all()
    return {"themes": [{"id": t.id, "name": t.name, "description": t.description, "price": t.price, "premium": t.premium} for t in themes]}

@router.get("/{theme_id}")
async def get_theme(
    theme_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific theme"""
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    return {"id": theme.id, "name": theme.name, "description": theme.description, "css_url": theme.css_url, "price": theme.price, "premium": theme.premium}

@router.post("/{theme_id}/apply")
async def apply_theme(
    theme_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply a theme to user's profile"""
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    
    # Check if user has premium access for premium themes
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not user_profile:
        user_profile = UserProfile(user_id=current_user.id)
        db.add(user_profile)
    
    if theme.premium:
        if not user_profile.premium_until or user_profile.premium_until < datetime.utcnow():
            raise HTTPException(status_code=403, detail="Premium subscription required")
    
    user_profile.theme_id = theme_id
    db.commit()
    
    return {"message": "Theme applied successfully", "theme_id": theme_id}

@router.get("/my/current")
async def get_current_theme(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's current theme"""
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not user_profile or not user_profile.theme_id:
        return {"theme": None}
    
    theme = db.query(Theme).filter(Theme.id == user_profile.theme_id).first()
    return {"theme": {"id": theme.id, "name": theme.name, "css_url": theme.css_url}}
