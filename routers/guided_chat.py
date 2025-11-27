from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from database import SessionLocal
from models import GuidedChatSession, User
from auth import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/guided-chat", tags=["Guided Chat"])


class StartSessionRequest(BaseModel):
    topic: str = None

@router.post("/start")
async def start_session(
    request: StartSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new guided chat session"""
    # Check if user has an active session
    active_session = db.query(GuidedChatSession).filter(
        GuidedChatSession.user_id == current_user.id,
        GuidedChatSession.ended_at == None
    ).first()
    
    if active_session:
        raise HTTPException(status_code=400, detail="You already have an active session")
    
    session = GuidedChatSession(
        user_id=current_user.id,
        topic=request.topic
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return {
        "id": session.id,
        "topic": session.topic,
        "started_at": session.started_at.isoformat(),
        "message": "Guided chat session started"
    }

@router.post("/{session_id}/end")
async def end_session(
    session_id: int,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """End a guided chat session"""
    session = db.query(GuidedChatSession).filter(
        GuidedChatSession.id == session_id,
        GuidedChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.ended_at:
        raise HTTPException(status_code=400, detail="Session already ended")
    
    session.ended_at = datetime.utcnow()
    if notes:
        session.notes = notes
    db.commit()
    
    duration_minutes = int((session.ended_at - session.started_at).total_seconds() / 60)
    
    return {
        "message": "Session ended successfully",
        "duration_minutes": duration_minutes
    }

@router.get("/my/sessions")
async def get_my_sessions(
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's guided chat sessions"""
    query = db.query(GuidedChatSession).filter(GuidedChatSession.user_id == current_user.id)
    
    if active_only:
        query = query.filter(GuidedChatSession.ended_at == None)
    
    sessions = query.order_by(GuidedChatSession.started_at.desc()).all()
    
    return {
        "sessions": [
            {
                "id": s.id,
                "topic": s.topic,
                "started_at": s.started_at.isoformat(),
                "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                "is_active": s.ended_at is None
            }
            for s in sessions
        ]
    }

@router.get("/coaches")
async def get_available_coaches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of available coaches (users with is_coach flag)"""
    # For now, return empty list - can be enhanced later
    # In a real implementation, you'd have a is_coach flag on User model
    return {"coaches": []}
