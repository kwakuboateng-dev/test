from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import User as UserSchema
from auth import oauth2_scheme, decode_access_token

router = APIRouter(prefix="/users", tags=["users"])

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/me", response_model=UserSchema)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me")
def update_my_profile(
    real_name: str = None,
    preferences: dict = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if real_name:
        current_user.real_name = real_name
    if preferences:
        current_user.preferences = preferences
    
    db.commit()
    db.refresh(current_user)
    return current_user
