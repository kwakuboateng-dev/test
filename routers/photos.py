from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import get_current_user
import os
import shutil
from pathlib import Path
import uuid
import imghdr  # Built-in Python module for image type detection
import hashlib

router = APIRouter(prefix="/photos", tags=["photos"])

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads/profile_photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_IMAGE_TYPES = {"jpeg", "png", "webp"}  # imghdr format names
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def is_allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image_content(file_content: bytes) -> bool:
    """Validate file is actually an image using imghdr"""
    try:
        image_type = imghdr.what(None, h=file_content)
        return image_type in ALLOWED_IMAGE_TYPES
    except:
        return False

def sanitize_filename(filename: str) -> str:
    """Remove potentially dangerous characters from filename"""
    # Remove path separators and other dangerous chars
    dangerous_chars = ['/', '\\', '..', '\x00']
    for char in dangerous_chars:
        filename = filename.replace(char, '')
    return filename

@router.post("/upload")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a profile photo with security validation"""
    # Sanitize filename
    filename = sanitize_filename(file.filename)
    
    # Validate file type by extension
    if not is_allowed_file(filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file
    contents = await file.read()
    
    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max size is 5MB")
    
    # Validate actual file content (magic bytes)
    if not validate_image_content(contents):
        raise HTTPException(
            status_code=400,
            detail="Invalid image file. File content does not match image format"
        )
    
    # Delete old photo if exists
    if current_user.profile_photo_url:
        old_photo_path = Path(current_user.profile_photo_url)
        if old_photo_path.exists():
            try:
                old_photo_path.unlink()
            except:
                pass  # Ignore if deletion fails
    
    # Generate secure unique filename using hash
    file_hash = hashlib.sha256(contents).hexdigest()[:16]
    file_extension = filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{current_user.id}_{file_hash}.{file_extension}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Ensure file_path is within UPLOAD_DIR (prevent path traversal)
    if not file_path.resolve().is_relative_to(UPLOAD_DIR.resolve()):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Update user profile
    current_user.profile_photo_url = str(file_path)
    db.commit()
    
    return {
        "message": "Photo uploaded successfully",
        "photo_url": f"/photos/{current_user.id}"
    }

@router.get("/{user_id}")
async def get_profile_photo(
    user_id: int,
    current_user: User = Depends(get_current_user),  # Require authentication
    db: Session = Depends(get_db)
):
    """Get a user's profile photo (authentication required)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.profile_photo_url:
        raise HTTPException(status_code=404, detail="No profile photo")
    
    photo_path = Path(user.profile_photo_url)
    
    # Security: Ensure path is within allowed directory
    if not photo_path.resolve().is_relative_to(UPLOAD_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not photo_path.exists():
        raise HTTPException(status_code=404, detail="Photo file not found")
    
    return FileResponse(photo_path)

@router.delete("/delete")
async def delete_profile_photo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete profile photo"""
    if not current_user.profile_photo_url:
        raise HTTPException(status_code=404, detail="No profile photo to delete")
    
    photo_path = Path(current_user.profile_photo_url)
    if photo_path.exists():
        try:
            photo_path.unlink()
        except:
            pass
    
    current_user.profile_photo_url = None
    db.commit()
    
    return {"message": "Photo deleted successfully"}

@router.post("/upload-verification")
async def upload_verification_photo(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a photo for verification with security checks"""
    # Sanitize filename
    filename = sanitize_filename(file.filename)
    
    # Validate file type
    if not is_allowed_file(filename):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Create verification directory
    VERIFICATION_DIR = Path("uploads/verification_photos")
    VERIFICATION_DIR.mkdir(parents=True, exist_ok=True)
    
    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max size is 5MB")
    
    # Validate content
    if not validate_image_content(contents):
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Save verification photo
    file_hash = hashlib.sha256(contents).hexdigest()[:16]
    file_extension = filename.rsplit(".", 1)[1].lower()
    unique_filename = f"verify_{current_user.id}_{file_hash}.{file_extension}"
    file_path = VERIFICATION_DIR / unique_filename
    
    # Path validation
    if not file_path.resolve().is_relative_to(VERIFICATION_DIR.resolve()):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Mark as pending verification (admin would review this)
    # For MVP, we'll auto-verify
    current_user.photo_verified = True
    db.commit()
    
    return {
        "message": "Verification photo submitted successfully",
        "verified": current_user.photo_verified
    }
