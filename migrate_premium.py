"""
Migration script to add premium gamification tables to the database.
Run this script to create all new tables for badges, themes, icebreakers, mood tracking,
quizzes, nudges, events, tips, guided chat, and emotional safety features.
"""

from database import engine, Base
from models import (
    Badge, UserProfile, Theme, IcebreakerPrompt, UserIcebreaker,
    MoodCheckIn, CompatibilityQuiz, UserQuizResult, Nudge, UserNudgeLog,
    Event, UserEventRegistration, RelationshipTip, GuidedChatSession,
    EmotionalSafetySetting
)

def migrate_premium_features():
    """Create all premium gamification tables"""
    print("Creating premium gamification tables...")
    
    # This will create only the tables that don't exist yet
    Base.metadata.create_all(bind=engine)
    
    print("✅ Premium gamification tables created successfully!")
    print("\nNew tables added:")
    print("  - badges")
    print("  - user_profiles")
    print("  - themes")
    print("  - icebreaker_prompts")
    print("  - user_icebreakers")
    print("  - mood_checkins")
    print("  - compatibility_quizzes")
    print("  - user_quiz_results")
    print("  - nudges")
    print("  - user_nudge_logs")
    print("  - events")
    print("  - user_event_registrations")
    print("  - relationship_tips")
    print("  - guided_chat_sessions")
    print("  - emotional_safety_settings")

if __name__ == "__main__":
    migrate_premium_features()
