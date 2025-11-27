from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from database import get_db
from models import MoodCheckIn, User
from auth import get_current_user
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter(prefix="/mood", tags=["Mood"])


class MoodCheckInCreate(BaseModel):
    mood: str  # happy, sad, anxious, excited, calm, stressed
    notes: str = None

@router.post("/checkin")
async def create_mood_checkin(
    mood_data: MoodCheckInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new mood check-in"""
    checkin = MoodCheckIn(
        user_id=current_user.id,
        mood=mood_data.mood,
        notes=mood_data.notes
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    
    return {"id": checkin.id, "mood": checkin.mood, "date": checkin.date.isoformat(), "message": "Mood check-in recorded"}

@router.get("/history")
async def get_mood_history(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's mood check-in history"""
    since_date = datetime.utcnow() - timedelta(days=days)
    checkins = db.query(MoodCheckIn).filter(
        MoodCheckIn.user_id == current_user.id,
        MoodCheckIn.date >= since_date
    ).order_by(MoodCheckIn.date.desc()).all()
    
    return {
        "checkins": [
            {"id": c.id, "mood": c.mood, "date": c.date.isoformat(), "notes": c.notes}
            for c in checkins
        ]
    }

@router.get("/today")
async def get_today_mood(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get today's mood check-in"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    checkin = db.query(MoodCheckIn).filter(
        MoodCheckIn.user_id == current_user.id,
        MoodCheckIn.date >= today_start
    ).first()
    
    if not checkin:
        return {"checkin": None, "checked_in_today": False}
    
    return {
        "checkin": {"id": checkin.id, "mood": checkin.mood, "date": checkin.date.isoformat(), "notes": checkin.notes},
        "checked_in_today": True
    }

@router.get("/moods")
async def get_available_moods():
    """Get list of available mood options"""
    return {
        "moods": [
            {"value": "happy", "emoji": "😊", "label": "Happy"},
            {"value": "sad", "emoji": "😢", "label": "Sad"},
            {"value": "anxious", "emoji": "😰", "label": "Anxious"},
            {"value": "excited", "emoji": "🤩", "label": "Excited"},
            {"value": "calm", "emoji": "😌", "label": "Calm"},
            {"value": "stressed", "emoji": "😫", "label": "Stressed"},
            {"value": "loved", "emoji": "🥰", "label": "Loved"},
            {"value": "lonely", "emoji": "😔", "label": "Lonely"}
        ]
    }
