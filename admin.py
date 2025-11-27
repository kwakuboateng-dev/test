from sqladmin import ModelView, Admin
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from models import (
    User, Match, Message, Mission, Block, Report,
    Badge, UserProfile, Theme, IcebreakerPrompt, UserIcebreaker,
    MoodCheckIn, CompatibilityQuiz, UserQuizResult, Nudge, UserNudgeLog,
    Event, UserEventRegistration, RelationshipTip, GuidedChatSession,
    EmotionalSafetySetting
)
from auth import verify_password, get_password_hash
from database import SessionLocal
import os

# Authentication Backend
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        db = SessionLocal()
        # Try to find user by email first, then by anonymous_handle (username)
        user = db.query(User).filter((User.email == email) | (User.anonymous_handle == email)).first()
        db.close()

        if user and verify_password(password, user.hashed_password):
            if user.is_superuser:
                request.session.update({"token": user.email})
                return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return RedirectResponse(url="/admin/login", status_code=302)

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        return True

# Custom Admin Class
class OdoyewuAdmin(Admin):
    async def index(self, request: Request):
        # Fetch stats
        db = SessionLocal()
        users_count = db.query(User).count()
        matches_count = db.query(Match).count()
        messages_count = db.query(Message).count()
        reports_count = db.query(Report).filter(Report.status == "pending").count()
        db.close()
        
        return await self.templates.TemplateResponse(
            request, 
            "dashboard.html", 
            context={
                "request": request,
                "users_count": users_count,
                "matches_count": matches_count,
                "messages_count": messages_count,
                "reports_count": reports_count
            }
        )

# Base Secure Model View
class SecureModelView(ModelView):
    def is_accessible(self, request: Request) -> bool:
        return request.session.get("token") is not None

class UserAdmin(SecureModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    
    column_list = [User.id, User.email, User.anonymous_handle, User.is_superuser, User.level, User.xp, User.verified, User.created_at]
    column_searchable_list = [User.email, User.anonymous_handle]
    column_sortable_list = [User.id, User.email, User.level, User.xp, User.created_at]
    column_default_sort = [("created_at", True)]
    
    form_columns = [
        User.email,
        User.anonymous_handle,
        User.real_name,
        User.bio,
        User.interests,
        User.mood_status,
        User.verified,
        User.is_superuser,
        User.xp,
        User.level,
        User.photo_verified,
        User.hashed_password
    ]

    # Hash password on save
    async def on_model_change(self, data, model, is_created, request):
        if "hashed_password" in data and data["hashed_password"]:
            data["hashed_password"] = get_password_hash(data["hashed_password"])

class MatchAdmin(SecureModelView, model=Match):
    name = "Match"
    name_plural = "Matches"
    icon = "fa-solid fa-heart"
    
    column_list = [Match.id, Match.user_a_id, Match.user_b_id, Match.status, Match.created_at]
    column_searchable_list = [Match.status]
    column_sortable_list = [Match.id, Match.created_at]
    
    form_columns = [
        Match.user_a,
        Match.user_b,
        Match.status,
        Match.is_revealed_a,
        Match.is_revealed_b,
    ]

class MessageAdmin(SecureModelView, model=Message):
    name = "Message"
    name_plural = "Messages"
    icon = "fa-solid fa-comment"
    
    column_list = [Message.id, Message.match_id, Message.sender_id, Message.content, Message.created_at]
    column_searchable_list = [Message.content]
    column_sortable_list = [Message.id, Message.created_at]
    column_default_sort = [("created_at", True)]
    
    form_columns = [
        Message.match,
        Message.sender,
        Message.content,
    ]

class MissionAdmin(SecureModelView, model=Mission):
    name = "Mission"
    name_plural = "Missions"
    icon = "fa-solid fa-trophy"
    
    column_list = [Mission.id, Mission.user_id, Mission.mission_type, Mission.completed, Mission.xp_reward, Mission.created_at]
    column_searchable_list = [Mission.mission_type]
    column_sortable_list = [Mission.id, Mission.created_at, Mission.completed]
    
    form_columns = [
        Mission.user,
        Mission.mission_type,
        Mission.completed,
        Mission.xp_reward,
        Mission.completed_at,
    ]

class BlockAdmin(SecureModelView, model=Block):
    name = "Block"
    name_plural = "Blocks"
    icon = "fa-solid fa-ban"
    
    column_list = [Block.id, Block.user_id, Block.blocked_user_id, Block.reason, Block.created_at]
    column_searchable_list = [Block.reason]
    column_sortable_list = [Block.id, Block.created_at]
    
    form_columns = [
        Block.user,
        Block.blocked_user,
        Block.reason,
    ]

class ReportAdmin(SecureModelView, model=Report):
    name = "Report"
    name_plural = "Reports"
    icon = "fa-solid fa-flag"
    
    column_list = [Report.id, Report.reporter_id, Report.reported_user_id, Report.report_type, Report.status, Report.created_at]
    column_searchable_list = [Report.report_type, Report.description, Report.status]
    column_sortable_list = [Report.id, Report.created_at, Report.status]
    column_default_sort = [("created_at", True)]
    
    form_columns = [
        Report.reporter,
        Report.reported_user,
        Report.report_type,
        Report.description,
        Report.status,
    ]

# Premium & Gamification Admin Views

class BadgeAdmin(SecureModelView, model=Badge):
    name = "Badge"
    name_plural = "Badges"
    icon = "fa-solid fa-medal"
    
    column_list = ["id", "name", "xp_requirement", "created_at"]
    column_searchable_list = ["name"]
    column_sortable_list = ["id", "name", "xp_requirement", "created_at"]
    
    form_columns = ["name", "description", "icon_url", "xp_requirement"]

class UserProfileAdmin(SecureModelView, model=UserProfile):
    name = "User Profile"
    name_plural = "User Profiles"
    icon = "fa-solid fa-id-card"
    
    column_list = ["id", "user_id", "theme_id", "premium_until", "created_at"]
    column_sortable_list = ["id", "user_id", "premium_until", "created_at"]
    
    form_columns = ["user", "theme", "premium_until"]

class ThemeAdmin(SecureModelView, model=Theme):
    name = "Theme"
    name_plural = "Themes"
    icon = "fa-solid fa-palette"
    
    column_list = ["id", "name", "price", "premium", "created_at"]
    column_searchable_list = ["name"]
    column_sortable_list = ["id", "name", "price", "created_at"]
    
    form_columns = ["name", "description", "css_url", "price", "premium"]

class IcebreakerPromptAdmin(SecureModelView, model=IcebreakerPrompt):
    name = "Icebreaker Prompt"
    name_plural = "Icebreaker Prompts"
    icon = "fa-solid fa-message"
    
    column_list = ["id", "category", "premium", "created_at"]
    column_searchable_list = ["text", "category"]
    column_sortable_list = ["id", "category", "created_at"]
    
    form_columns = ["text", "category", "premium"]

class MoodCheckInAdmin(SecureModelView, model=MoodCheckIn):
    name = "Mood Check-in"
    name_plural = "Mood Check-ins"
    icon = "fa-solid fa-face-smile"
    
    column_list = ["id", "user_id", "mood", "date"]
    column_searchable_list = ["mood"]
    column_sortable_list = ["id", "date"]
    column_default_sort = [("date", True)]
    
    form_columns = ["user", "mood", "notes"]

class CompatibilityQuizAdmin(SecureModelView, model=CompatibilityQuiz):
    name = "Compatibility Quiz"
    name_plural = "Compatibility Quizzes"
    icon = "fa-solid fa-clipboard-question"
    
    column_list = ["id", "title", "premium", "created_at"]
    column_searchable_list = ["title"]
    column_sortable_list = ["id", "title", "created_at"]
    
    form_columns = ["title", "description", "questions", "premium"]

class UserQuizResultAdmin(SecureModelView, model=UserQuizResult):
    name = "Quiz Result"
    name_plural = "Quiz Results"
    icon = "fa-solid fa-chart-line"
    
    column_list = ["id", "user_id", "quiz_id", "score", "completed_at"]
    column_sortable_list = ["id", "score", "completed_at"]
    column_default_sort = [("completed_at", True)]
    
    form_columns = ["user", "quiz", "answers", "score"]

class NudgeAdmin(SecureModelView, model=Nudge):
    name = "Nudge"
    name_plural = "Nudges"
    icon = "fa-solid fa-bell"
    
    column_list = ["id", "type", "premium", "active", "created_at"]
    column_searchable_list = ["type", "message"]
    column_sortable_list = ["id", "type", "created_at"]
    
    form_columns = ["type", "message", "premium", "active"]

class EventAdmin(SecureModelView, model=Event):
    name = "Event"
    name_plural = "Events"
    icon = "fa-solid fa-calendar-days"
    
    column_list = ["id", "title", "start_time", "end_time", "premium", "max_participants"]
    column_searchable_list = ["title"]
    column_sortable_list = ["id", "start_time", "end_time"]
    column_default_sort = [("start_time", True)]
    
    form_columns = ["title", "description", "start_time", "end_time", "premium", "max_participants"]

class UserEventRegistrationAdmin(SecureModelView, model=UserEventRegistration):
    name = "Event Registration"
    name_plural = "Event Registrations"
    icon = "fa-solid fa-user-check"
    
    column_list = ["id", "user_id", "event_id", "registered_at"]
    column_sortable_list = ["id", "registered_at"]
    column_default_sort = [("registered_at", True)]
    
    form_columns = ["user", "event"]

class RelationshipTipAdmin(SecureModelView, model=RelationshipTip):
    name = "Relationship Tip"
    name_plural = "Relationship Tips"
    icon = "fa-solid fa-lightbulb"
    
    column_list = ["id", "title", "category", "premium", "created_at"]
    column_searchable_list = ["title", "content"]
    column_sortable_list = ["id", "title", "category", "created_at"]
    
    form_columns = ["title", "content", "category", "premium"]

class GuidedChatSessionAdmin(SecureModelView, model=GuidedChatSession):
    name = "Guided Chat Session"
    name_plural = "Guided Chat Sessions"
    icon = "fa-solid fa-comments"
    
    column_list = ["id", "user_id", "coach_id", "topic", "started_at", "ended_at"]
    column_searchable_list = ["topic"]
    column_sortable_list = ["id", "started_at", "ended_at"]
    column_default_sort = [("started_at", True)]
    
    form_columns = ["user", "coach", "topic", "notes", "ended_at"]

class EmotionalSafetySettingAdmin(SecureModelView, model=EmotionalSafetySetting):
    name = "Emotional Safety Setting"
    name_plural = "Emotional Safety Settings"
    icon = "fa-solid fa-shield-heart"
    
    column_list = ["id", "user_id", "chat_time_limit_minutes", "auto_end_enabled", "require_check_in"]
    column_sortable_list = ["id", "user_id"]
    
    form_columns = ["user", "chat_time_limit_minutes", "auto_end_enabled", "require_check_in"]
