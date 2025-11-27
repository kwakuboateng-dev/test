from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Match, Message
from routers.users import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])

class MessageCreate(BaseModel):
    content: str

@router.get("/match/{match_id}/messages")
def get_messages(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages for a specific match."""
    # Verify user is part of this match
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.user_a_id != current_user.id and match.user_b_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    messages = db.query(Message).filter(Message.match_id == match_id).order_by(Message.timestamp).all()
    
    return [{
        "id": msg.id,
        "sender_id": msg.sender_id,
        "content": msg.content,
        "timestamp": msg.timestamp,
        "is_mine": msg.sender_id == current_user.id
    } for msg in messages]

@router.post("/match/{match_id}/send")
def send_message(
    match_id: int,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a match."""
    # Verify user is part of this match
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.user_a_id != current_user.id and match.user_b_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_message = Message(
        match_id=match_id,
        sender_id=current_user.id,
        content=message.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return {
        "id": new_message.id,
        "content": new_message.content,
        "timestamp": new_message.timestamp
    }
