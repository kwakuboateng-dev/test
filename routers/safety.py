from fastapi import APIRouter, Depends, HTTPException, status, Query
from database import get_db
from models import User, Block, Report
from auth import get_current_user
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/safety", tags=["safety"])

@router.post("/block/{user_id}")
def block_user(user_id: int, reason: Optional[str] = Query(None), db = Depends(get_db), current_user = Depends(get_current_user)):
    """Block a user"""
    # Check if user exists
    blocked_user = db.query(User).filter(User.id == user_id).first()
    if not blocked_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Can't block yourself
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot block yourself")
    
    # Check if already blocked
    existing_block = db.query(Block).filter(
        Block.user_id == current_user.id,
        Block.blocked_user_id == user_id
    ).first()
    
    if existing_block:
        raise HTTPException(status_code=400, detail="User already blocked")
    
    # Create block
    new_block = Block(
        user_id=current_user.id,
        blocked_user_id=user_id,
        reason=reason
    )
    db.add(new_block)
    db.commit()
    
    return {"message": "User blocked successfully"}

@router.delete("/unblock/{user_id}")
def unblock_user(user_id: int, db = Depends(get_db), current_user = Depends(get_current_user)):
    """Unblock a user"""
    block = db.query(Block).filter(
        Block.user_id == current_user.id,
        Block.blocked_user_id == user_id
    ).first()
    
    if not block:
        raise HTTPException(status_code=404, detail="User is not blocked")
    
    db.delete(block)
    db.commit()
    
    return {"message": "User unblocked successfully"}

@router.get("/blocked-users")
def get_blocked_users(db = Depends(get_db), current_user = Depends(get_current_user)):
    """Get list of blocked users"""
    blocks = db.query(Block).filter(Block.user_id == current_user.id).all()
    
    blocked_users = []
    for block in blocks:
        user = db.query(User).filter(User.id == block.blocked_user_id).first()
        if user:
            blocked_users.append({
                "id": user.id,
                "anonymous_handle": user.anonymous_handle,
                "blocked_at": block.created_at,
                "reason": block.reason
            })
    
    return blocked_users

@router.post("/report/{user_id}")
def report_user(
    user_id: int,
    report_type: str = Query(...),
    description: Optional[str] = Query(None),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Report a user for inappropriate behavior"""
    # Validate report type
    valid_types = ["harassment", "spam", "inappropriate", "fake_profile", "other"]
    if report_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid report type. Must be one of: {', '.join(valid_types)}")
    
    # Check if user exists
    reported_user = db.query(User).filter(User.id == user_id).first()
    if not reported_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Can't report yourself
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot report yourself")
    
    # Create report
    new_report = Report(
        reporter_id=current_user.id,
        reported_user_id=user_id,
        report_type=report_type,
        description=description,
        status="pending"
    )
    db.add(new_report)
    db.commit()
    
    return {"message": "Report submitted successfully. Our team will review it shortly."}

@router.get("/my-reports")
def get_my_reports(db = Depends(get_db), current_user = Depends(get_current_user)):
    """Get user's submitted reports"""
    reports = db.query(Report).filter(Report.reporter_id == current_user.id).all()
    
    return [{
        "id": report.id,
        "reported_user_id": report.reported_user_id,
        "report_type": report.report_type,
        "description": report.description,
        "status": report.status,
        "created_at": report.created_at
    } for report in reports]
