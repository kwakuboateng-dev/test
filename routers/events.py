from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from database import SessionLocal
from models import Event, UserEventRegistration, User, UserProfile
from auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("/")
async def get_events(
    upcoming_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all events"""
    query = db.query(Event)
    
    if upcoming_only:
        query = query.filter(Event.start_time > datetime.utcnow())
    
    query = query.order_by(Event.start_time)
    events = query.all()
    
    # Get user's registrations
    user_registrations = db.query(UserEventRegistration).filter(
        UserEventRegistration.user_id == current_user.id
    ).all()
    registered_event_ids = {r.event_id for r in user_registrations}
    
    return {
        "events": [
            {
                "id": e.id,
                "title": e.title,
                "description": e.description,
                "start_time": e.start_time.isoformat(),
                "end_time": e.end_time.isoformat(),
                "premium": e.premium,
                "max_participants": e.max_participants,
                "is_registered": e.id in registered_event_ids,
                "participants_count": db.query(UserEventRegistration).filter(UserEventRegistration.event_id == e.id).count()
            }
            for e in events
        ]
    }

@router.get("/{event_id}")
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get event details"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    participants_count = db.query(UserEventRegistration).filter(UserEventRegistration.event_id == event_id).count()
    is_registered = db.query(UserEventRegistration).filter(
        UserEventRegistration.event_id == event_id,
        UserEventRegistration.user_id == current_user.id
    ).first() is not None
    
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "start_time": event.start_time.isoformat(),
        "end_time": event.end_time.isoformat(),
        "premium": event.premium,
        "max_participants": event.max_participants,
        "participants_count": participants_count,
        "is_registered": is_registered,
        "is_full": event.max_participants and participants_count >= event.max_participants
    }

@router.post("/{event_id}/register")
async def register_for_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register for an event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if event is premium
    if event.premium:
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        has_premium = user_profile and user_profile.premium_until and user_profile.premium_until > datetime.utcnow()
        if not has_premium:
            raise HTTPException(status_code=403, detail="Premium subscription required")
    
    # Check if already registered
    existing = db.query(UserEventRegistration).filter(
        UserEventRegistration.event_id == event_id,
        UserEventRegistration.user_id == current_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already registered for this event")
    
    # Check if event is full
    if event.max_participants:
        participants_count = db.query(UserEventRegistration).filter(UserEventRegistration.event_id == event_id).count()
        if participants_count >= event.max_participants:
            raise HTTPException(status_code=400, detail="Event is full")
    
    registration = UserEventRegistration(user_id=current_user.id, event_id=event_id)
    db.add(registration)
    db.commit()
    
    return {"message": "Successfully registered for event", "event_id": event_id}

@router.delete("/{event_id}/unregister")
async def unregister_from_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Unregister from an event"""
    registration = db.query(UserEventRegistration).filter(
        UserEventRegistration.event_id == event_id,
        UserEventRegistration.user_id == current_user.id
    ).first()
    
    if not registration:
        raise HTTPException(status_code=404, detail="Not registered for this event")
    
    db.delete(registration)
    db.commit()
    
    return {"message": "Successfully unregistered from event"}

@router.get("/my/registrations")
async def get_my_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's event registrations"""
    registrations = db.query(UserEventRegistration).filter(
        UserEventRegistration.user_id == current_user.id
    ).all()
    
    events = []
    for reg in registrations:
        event = db.query(Event).filter(Event.id == reg.event_id).first()
        if event:
            events.append({
                "id": event.id,
                "title": event.title,
                "start_time": event.start_time.isoformat(),
                "registered_at": reg.registered_at.isoformat()
            })
    
    return {"registrations": events}
