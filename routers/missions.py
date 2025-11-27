from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Mission
from auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/missions", tags=["missions"])

# Expanded mission pool with weekly rotation
MISSION_POOL = {
    "monday": [
        {"type": "start_conversation", "description": "Start 2 conversations", "xp": 15},
        {"type": "add_match", "description": "Add a new match", "xp": 15},
        {"type": "send_messages", "description": "Send 5 messages", "xp": 10},
    ],
    "tuesday": [
        {"type": "check_hotspots", "description": "Check the hotspot map", "xp": 10},
        {"type": "update_location", "description": "Update your location", "xp": 10},
        {"type": "visit_nearby", "description": "View 3 nearby users", "xp": 15},
    ],
    "wednesday": [
        {"type": "update_profile", "description": "Update your bio or interests", "xp": 15},
        {"type": "upload_photo", "description": "Upload or update profile photo", "xp": 20},
        {"type": "set_mood", "description": "Set your mood status", "xp": 10},
    ],
    "thursday": [
        {"type": "reveal_identity", "description": "Reveal your identity to someone", "xp": 25},
        {"type": "accept_match", "description": "Accept a match request", "xp": 15},
        {"type": "long_conversation", "description": "Have a 10+ message conversation", "xp": 20},
    ],
    "friday": [
        {"type": "weekend_prep", "description": "Update profile for weekend", "xp": 15},
        {"type": "browse_profiles", "description": "View 5 user profiles", "xp": 10},
        {"type": "active_chat", "description": "Chat with 3 different matches", "xp": 20},
    ],
    "saturday": [
        {"type": "weekend_warrior", "description": "Send 10 messages today", "xp": 20},
        {"type": "new_connections", "description": "Add 2 new matches", "xp": 25},
        {"type": "explore_hotspots", "description": "Check hotspots in your area", "xp": 15},
    ],
    "sunday": [
        {"type": "weekly_review", "description": "Review your matches", "xp": 10},
        {"type": "complete_profile", "description": "Ensure profile is 100% complete", "xp": 20},
        {"type": "plan_week", "description": "Set mood for the week ahead", "xp": 15},
    ],
}

# Special event missions (can be added to any day)
SPECIAL_MISSIONS = [
    {"type": "first_reveal", "description": "Make your first identity reveal", "xp": 50, "one_time": True},
    {"type": "verified_user", "description": "Verify your photo", "xp": 30, "one_time": True},
    {"type": "social_butterfly", "description": "Have 5 active matches", "xp": 40, "milestone": True},
]

def get_day_of_week():
    """Get current day of week in lowercase"""
    return datetime.utcnow().strftime("%A").lower()

@router.get("/daily")
def get_daily_missions(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get today's missions based on day of week."""
    # Get user's missions for today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    user_missions = db.query(Mission).filter(
        Mission.user_id == current_user.id,
        Mission.created_at >= today_start
    ).all()
    
    # Get missions for current day
    day_of_week = get_day_of_week()
    daily_missions = MISSION_POOL.get(day_of_week, MISSION_POOL["monday"])
    
    # If no missions exist for today, create them
    if not user_missions:
        for mission_def in daily_missions:
            new_mission = Mission(
                user_id=current_user.id,
                mission_type=mission_def["type"],
                xp_reward=mission_def["xp"],
                completed=False
            )
            db.add(new_mission)
        db.commit()
        
        # Refresh query
        user_missions = db.query(Mission).filter(
            Mission.user_id == current_user.id,
            Mission.created_at >= today_start
        ).all()
    
    # Format response
    result = []
    for mission in user_missions:
        mission_def = next((m for m in daily_missions if m["type"] == mission.mission_type), None)
        if mission_def:
            result.append({
                "id": mission.id,
                "type": mission.mission_type,
                "description": mission_def["description"],
                "xp_reward": mission.xp_reward,
                "completed": mission.completed,
                "day": day_of_week.capitalize()
            })
    
    return {
        "day": day_of_week.capitalize(),
        "missions": result,
        "total_xp_available": sum(m.xp_reward for m in user_missions if not m.completed)
    }

@router.get("/weekly-preview")
def get_weekly_preview(current_user = Depends(get_current_user)):
    """Preview missions for the entire week"""
    weekly_schedule = {}
    
    for day, missions in MISSION_POOL.items():
        total_xp = sum(m["xp"] for m in missions)
        weekly_schedule[day] = {
            "missions": [
                {"description": m["description"], "xp": m["xp"]} 
                for m in missions
            ],
            "total_xp": total_xp
        }
    
    return {
        "weekly_schedule": weekly_schedule,
        "total_weekly_xp": sum(s["total_xp"] for s in weekly_schedule.values())
    }

@router.post("/complete/{mission_id}")
def complete_mission(
    mission_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Mark a mission as completed and award XP."""
    mission = db.query(Mission).filter(
        Mission.id == mission_id,
        Mission.user_id == current_user.id
    ).first()
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    if mission.completed:
        return {"message": "Mission already completed", "already_completed": True}
    
    # Mark as completed
    mission.completed = True
    mission.completed_at = datetime.utcnow()
    
    # Award XP
    current_user.xp += mission.xp_reward
    
    # Level up logic (every 100 XP = 1 level)
    new_level = (current_user.xp // 100) + 1
    leveled_up = False
    if new_level > current_user.level:
        current_user.level = new_level
        leveled_up = True
    
    db.commit()
    
    return {
        "message": "Mission completed! 🎉",
        "xp_earned": mission.xp_reward,
        "total_xp": current_user.xp,
        "level": current_user.level,
        "leveled_up": leveled_up,
        "xp_to_next_level": (new_level * 100) - current_user.xp
    }

@router.get("/stats")
def get_mission_stats(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get user's mission completion statistics"""
    # Get all completed missions
    completed_missions = db.query(Mission).filter(
        Mission.user_id == current_user.id,
        Mission.completed == True
    ).all()
    
    # Get today's missions
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_missions = db.query(Mission).filter(
        Mission.user_id == current_user.id,
        Mission.created_at >= today_start
    ).all()
    
    today_completed = sum(1 for m in today_missions if m.completed)
    
    return {
        "total_missions_completed": len(completed_missions),
        "total_xp_earned": sum(m.xp_reward for m in completed_missions),
        "current_level": current_user.level,
        "current_xp": current_user.xp,
        "today_completed": today_completed,
        "today_total": len(today_missions),
        "completion_rate": f"{(today_completed / len(today_missions) * 100):.0f}%" if today_missions else "0%"
    }
