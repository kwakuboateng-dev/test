from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/register-token")
def register_push_token(
    token: str,
    platform: str,  # 'ios', 'android', 'web'
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register device push notification token"""
    current_user.push_token = token
    db.commit()
    
    return {
        "message": "Push token registered successfully",
        "platform": platform
    }

@router.delete("/unregister-token")
def unregister_push_token(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unregister push notification token"""
    current_user.push_token = None
    db.commit()
    
    return {"message": "Push token unregistered"}

# Notification helper (to be used by other endpoints)
async def send_push_notification(user_id: int, title: str, body: str, data: dict, db: Session):
    """
    Send push notification to a user
    In production, integrate with:
    - Firebase Cloud Messaging (FCM) for iOS/Android
    - Web Push for web browsers
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.push_token:
        return False
    
    # TODO: Integrate with actual push service
    # For MVP, this is a placeholder
    print(f"📱 PUSH NOTIFICATION to User {user_id}:")
    print(f"   Title: {title}")
    print(f"   Body: {body}")
    print(f"   Data: {data}")
    
    return True
