from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User
from auth import get_current_user
from datetime import datetime, timedelta
import math

router = APIRouter(prefix="/hotspots", tags=["hotspots"])

def round_to_grid(latitude: float, longitude: float, grid_size: float = 0.1):
    """Round coordinates to a grid for privacy"""
    return (
        round(latitude / grid_size) * grid_size,
        round(longitude / grid_size) * grid_size
    )

@router.get("/areas")
def get_hotspot_areas(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get aggregated activity areas (privacy-safe hotspots)"""
    # Get users active in last 24 hours
    active_since = datetime.utcnow() - timedelta(hours=24)
    
    active_users = db.query(User).filter(
        User.latitude.isnot(None),
        User.longitude.isnot(None),
        User.last_location_update >= active_since
    ).all()
    
    # Aggregate into grid cells
    hotspots = {}
    for user in active_users:
        grid_lat, grid_lon = round_to_grid(user.latitude, user.longitude)
        key = (grid_lat, grid_lon)
        
        if key not in hotspots:
            hotspots[key] = {
                "latitude": grid_lat,
                "longitude": grid_lon,
                "count": 0
            }
        hotspots[key]["count"] += 1
    
    # Filter out areas with fewer than 3 users (privacy)
    filtered_hotspots = [
        spot for spot in hotspots.values()
        if spot["count"] >= 3
    ]
    
    return {
        "hotspots": filtered_hotspots,
        "updated_at": datetime.utcnow()
    }

@router.get("/nearby-activity")
def get_nearby_activity(
    radius: float = 10.0,  # miles
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get activity count within radius"""
    if not current_user.latitude or not current_user.longitude:
        raise HTTPException(status_code=400, detail="User location not set")
    
    active_since = datetime.utcnow() - timedelta(hours=24)
    
    # Simple count (in production, use spatial query)
    nearby_count = db.query(User).filter(
        User.id != current_user.id,
        User.latitude.isnot(None),
        User.longitude.isnot(None),
        User.last_location_update >= active_since
    ).count()
    
    return {
        "active_users_nearby": nearby_count,
        "radius_miles": radius
    }
