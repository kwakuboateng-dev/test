from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Match
from routers.users import get_current_user

router = APIRouter(prefix="/reveal", tags=["reveal"])

@router.post("/match/{match_id}/reveal")
def reveal_identity(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reveal your identity to a match."""
    # Get the match
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Verify user is part of this match
    if match.user_a_id != current_user.id and match.user_b_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update reveal status
    if match.user_a_id == current_user.id:
        if match.is_revealed_a:
            return {"message": "Already revealed"}
        match.is_revealed_a = True
    else:
        if match.is_revealed_b:
            return {"message": "Already revealed"}
        match.is_revealed_b = True
    
    db.commit()
    
    # Push notification can be implemented with services like Firebase Cloud Messaging
    # Example: send_push_notification(other_user_id, "Someone revealed their identity!")
    
    return {
        "message": "Identity revealed",
        "real_name": current_user.real_name,
        "email": current_user.email
    }

@router.get("/match/{match_id}/status")
def get_reveal_status(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check reveal status for a match."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.user_a_id != current_user.id and match.user_b_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Determine which user is the current user and which is the other
    if match.user_a_id == current_user.id:
        my_reveal = match.is_revealed_a
        their_reveal = match.is_revealed_b
        other_user_id = match.user_b_id
    else:
        my_reveal = match.is_revealed_b
        their_reveal = match.is_revealed_a
        other_user_id = match.user_a_id
    
    response = {
        "i_revealed": my_reveal,
        "they_revealed": their_reveal
    }
    
    # If they revealed, include their real info
    if their_reveal:
        other_user = db.query(User).filter(User.id == other_user_id).first()
        response["their_info"] = {
            "real_name": other_user.real_name,
            "email": other_user.email
        }
    
    return response
