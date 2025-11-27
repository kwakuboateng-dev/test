# recreate_db.py

from database import Base, engine
from models import (
    User, Match, Message, Mission, Block, Report,
    Badge, UserProfile, Theme, IcebreakerPrompt, UserIcebreaker,
    MoodCheckIn, CompatibilityQuiz, UserQuizResult,
    Nudge, UserNudgeLog, Event, UserEventRegistration,
    RelationshipTip, GuidedChatSession, EmotionalSafetySetting
)

def recreate():
    print("⚠️  Dropping ALL tables...")
    Base.metadata.drop_all(bind=engine)

    print("📦 Recreating tables...")
    Base.metadata.create_all(bind=engine)

    print("✅ Done! Database schema is fresh and clean.")


if __name__ == "__main__":
    recreate()
