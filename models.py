from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    anonymous_handle = Column(String, unique=True, index=True)
    verified = Column(Boolean, default=False)
    
    # Profile fields
    real_name = Column(String, nullable=True)
    bio = Column(String, nullable=True)
    interests = Column(String, nullable=True)
    mood_status = Column(String, nullable=True)
    
    # Location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    last_location_update = Column(DateTime, nullable=True)
    
    # Gamification
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    
    # Photo & Verification
    profile_photo_url = Column(String, nullable=True)
    photo_verified = Column(Boolean, default=False)
    
    # Push Notifications
    push_token = Column(String, nullable=True)
    
    # Admin
    is_superuser = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __str__(self):
        return self.anonymous_handle or self.email or str(self.id)

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_a_id = Column(Integer, ForeignKey("users.id"))
    user_b_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending")
    
    # Identity reveal tracking
    is_revealed_a = Column(Boolean, default=False)
    is_revealed_b = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user_a = relationship("User", foreign_keys=[user_a_id])
    user_b = relationship("User", foreign_keys=[user_b_id])
    messages = relationship("Message", back_populates="match")

    def __str__(self):
        return f"Match {self.id} ({self.status})"

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="messages")
    sender = relationship("User")

    def __str__(self):
        return f"Message {self.id}"

class Mission(Base):
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    mission_type = Column(String)
    completed = Column(Boolean, default=False)
    xp_reward = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User")

    def __str__(self):
        return f"{self.mission_type} ({'Done' if self.completed else 'Pending'})"

class Block(Base):
    __tablename__ = "blocks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    blocked_user_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])
    blocked_user = relationship("User", foreign_keys=[blocked_user_id])

    def __str__(self):
        return f"Block {self.id}"

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    reported_user_id = Column(Integer, ForeignKey("users.id"))
    report_type = Column(String)  # harassment, spam, inappropriate, fake_profile
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, reviewed, resolved
    created_at = Column(DateTime, default=datetime.utcnow)

    reporter = relationship("User", foreign_keys=[reporter_id])
    reported_user = relationship("User", foreign_keys=[reported_user_id])

    def __str__(self):
        return f"Report {self.id} ({self.status})"

# Premium & Gamification Models

class Badge(Base):
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text, nullable=True)
    icon_url = Column(String, nullable=True)
    xp_requirement = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return self.name

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    theme_id = Column(Integer, ForeignKey("themes.id"), nullable=True)
    premium_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    theme = relationship("Theme")

    def __str__(self):
        return f"Profile for {self.user_id}"

class Theme(Base):
    __tablename__ = "themes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text, nullable=True)
    css_url = Column(String, nullable=True)
    price = Column(Float, default=0.0)
    premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return self.name

class IcebreakerPrompt(Base):
    __tablename__ = "icebreaker_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    category = Column(String, nullable=True)  # casual, deep, fun, romantic
    premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f"{self.category}: {self.text[:50]}..."

class UserIcebreaker(Base):
    __tablename__ = "user_icebreakers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prompt_id = Column(Integer, ForeignKey("icebreaker_prompts.id"))
    used_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    prompt = relationship("IcebreakerPrompt")

    def __str__(self):
        return f"User {self.user_id} used prompt {self.prompt_id}"

class MoodCheckIn(Base):
    __tablename__ = "mood_checkins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    mood = Column(String)  # happy, sad, anxious, excited, calm, stressed
    notes = Column(Text, nullable=True)
    
    user = relationship("User")

    def __str__(self):
        return f"{self.mood} on {self.date.strftime('%Y-%m-%d')}"

class CompatibilityQuiz(Base):
    __tablename__ = "compatibility_quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    questions = Column(Text)  # JSON string
    premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return self.title

class UserQuizResult(Base):
    __tablename__ = "user_quiz_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("compatibility_quizzes.id"))
    answers = Column(Text)  # JSON string
    score = Column(Integer, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    quiz = relationship("CompatibilityQuiz")

    def __str__(self):
        return f"User {self.user_id} - Quiz {self.quiz_id}"

class Nudge(Base):
    __tablename__ = "nudges"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)  # engagement, match_alert, mission_reminder
    message = Column(Text)
    premium = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return f"{self.type}: {self.message[:50]}..."

class UserNudgeLog(Base):
    __tablename__ = "user_nudge_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    nudge_id = Column(Integer, ForeignKey("nudges.id"))
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    nudge = relationship("Nudge")

    def __str__(self):
        return f"Nudge {self.nudge_id} sent to {self.user_id}"

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    premium = Column(Boolean, default=False)
    max_participants = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return self.title

class UserEventRegistration(Base):
    __tablename__ = "user_event_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    registered_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")
    event = relationship("Event")

    def __str__(self):
        return f"User {self.user_id} registered for {self.event_id}"

class RelationshipTip(Base):
    __tablename__ = "relationship_tips"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    category = Column(String, nullable=True)  # communication, trust, intimacy, conflict
    premium = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return self.title

class GuidedChatSession(Base):
    __tablename__ = "guided_chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    coach_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    topic = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    
    user = relationship("User", foreign_keys=[user_id])
    coach = relationship("User", foreign_keys=[coach_id])

    def __str__(self):
        return f"Session {self.id} for User {self.user_id}"

class EmotionalSafetySetting(Base):
    __tablename__ = "emotional_safety_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    chat_time_limit_minutes = Column(Integer, nullable=True)
    auto_end_enabled = Column(Boolean, default=False)
    require_check_in = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User")

    def __str__(self):
        return f"Safety settings for User {self.user_id}"
