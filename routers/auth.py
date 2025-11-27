from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from models import User
from schemas import UserCreate, Token, User as UserSchema
from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from security import validate_password_strength, validate_email, sanitize_input, validate_username
from logging_config import logger

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserSchema)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """User registration with password strength validation"""
    
    # Validate email format
    email_valid, email_error = validate_email(user.email)
    if not email_valid:
        logger.warning(f"Invalid email format attempted: {user.email}")
        raise HTTPException(status_code=400, detail=email_error)
    
    # Validate password strength
    password_valid, password_error = validate_password_strength(user.password)
    if not password_valid:
        logger.warning(f"Weak password attempted for email: {user.email}")
        raise HTTPException(status_code=400, detail=password_error)
    
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        logger.warning(f"Duplicate email registration attempt: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate username format and reserved list
    username_valid, username_error = validate_username(user.anonymous_handle)
    if not username_valid:
        logger.warning(f"Invalid username attempted: {user.anonymous_handle}")
        raise HTTPException(status_code=400, detail=username_error)
    
    # Sanitize anonymous handle
    sanitized_handle = sanitize_input(user.anonymous_handle, max_length=30)
    if not sanitized_handle:
        raise HTTPException(status_code=400, detail="Invalid anonymous handle")
    
    # Check if handle is taken
    handle_exists = db.query(User).filter(User.anonymous_handle == sanitized_handle).first()
    if handle_exists:
        logger.warning(f"Duplicate handle registration attempt: {sanitized_handle}")
        raise HTTPException(status_code=400, detail="Anonymous handle already taken")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        anonymous_handle=sanitized_handle,
        hashed_password=hashed_password,
        verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user registered: {user.email}")
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Try to find user by email first, then by anonymous_handle
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        user = db.query(User).filter(User.anonymous_handle == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
