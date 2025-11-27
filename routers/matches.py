from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Match, Block
from routers.users import get_current_user
from utils import haversine_distance
from datetime import datetime, timedelta

router = APIRouter(prefix="/matches", tags=["matches"])

@router.post("/update-location")
def update_location(
    latitude: float,
    longitude: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's current location."""
    current_user.latitude = latitude
    current_user.longitude = longitude
    current_user.last_location_update = datetime.utcnow()
    db.commit()
    return {"message": "Location updated"}

@router.get("/nearby")
def get_nearby_users(
    radius: int = 50,  # Default radius in miles
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Find users within the specified radius, excluding blocked users."""
    if not current_user.latitude or not current_user.longitude:
        raise HTTPException(status_code=400, detail="User location not set")
    
    # Get blocked user IDs (users I blocked + users who blocked me)
    my_blocks = db.query(Block.blocked_user_id).filter(Block.user_id == current_user.id).all()
    blocked_me = db.query(Block.user_id).filter(Block.blocked_user_id == current_user.id).all()
    blocked_ids = set([b[0] for b in my_blocks] + [b[0] for b in blocked_me])
    
    # Get existing matches to exclude them from nearby
    existing_matches = db.query(Match).filter(
        ((Match.user_a_id == current_user.id) | (Match.user_b_id == current_user.id))
    ).all()
    matched_user_ids = set()
    for match in existing_matches:
        other_user_id = match.user_b_id if match.user_a_id == current_user.id else match.user_a_id
        matched_user_ids.add(other_user_id)
    
    # Get active users (active within last 72 hours)
    cutoff_time = datetime.utcnow() - timedelta(hours=72)
    active_users = db.query(User).filter(
        User.id != current_user.id,
        User.last_location_update >= cutoff_time,
        User.latitude.isnot(None),
        User.longitude.isnot(None),
        ~User.id.in_(blocked_ids),  # Exclude blocked users
        ~User.id.in_(matched_user_ids)  # Exclude already matched users
    ).all()
    
    # Filter by distance
    nearby_users = []
    for user in active_users:
        distance = haversine_distance(
            current_user.latitude,
            current_user.longitude,
            user.latitude,
            user.longitude
        )
        if distance <= radius:
            nearby_users.append({
                "id": user.id,
                "anonymous_handle": user.anonymous_handle,
                "bio": user.bio,
                "interests": user.interests,
                "mood_status": user.mood_status,
                "profile_photo_url": user.profile_photo_url,
                "distance": round(distance, 2)
            })
    
    return nearby_users

@router.post("/create")
def create_match(
    user_b_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a match between two users."""
    # Check if users are blocked
    is_blocked = db.query(Block).filter(
        ((Block.user_id == current_user.id) & (Block.blocked_user_id == user_b_id)) |
        ((Block.user_id == user_b_id) & (Block.blocked_user_id == current_user.id))
    ).first()
    
    if is_blocked:
        raise HTTPException(status_code=403, detail="Cannot create match with this user")
    
    # Check if match already exists
    existing_match = db.query(Match).filter(
        ((Match.user_a_id == current_user.id) & (Match.user_b_id == user_b_id)) |
        ((Match.user_a_id == user_b_id) & (Match.user_b_id == current_user.id))
    ).first()
    
    if existing_match:
        return {"message": "Match already exists", "match_id": existing_match.id}
    
    # Create new match
    new_match = Match(
        user_a_id=current_user.id,
        user_b_id=user_b_id,
        status="matched"
    )
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    
    return {"message": "Match created", "match_id": new_match.id}

@router.get("/my-matches")
def get_my_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all matches for the current user."""
    matches = db.query(Match).filter(
        ((Match.user_a_id == current_user.id) | (Match.user_b_id == current_user.id)) &
        (Match.status == "matched")
    ).all()
    
    result = []
    for match in matches:
        other_user_id = match.user_b_id if match.user_a_id == current_user.id else match.user_a_id
        other_user = db.query(User).filter(User.id == other_user_id).first()
        
        if other_user:
            result.append({
                "match_id": match.id,
                "user": {
                    "id": other_user.id,
                    "anonymous_handle": other_user.anonymous_handle,
                    "bio": other_user.bio,
                    "profile_photo_url": other_user.profile_photo_url
                },
                "created_at": match.created_at
            })
    
    return result
