from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from routers import (auth, users, matches, chat, reveal, missions, safety, photos, hotspots, notifications,
                     themes, icebreakers, mood, quizzes, events, tips, guided_chat, health)
from pathlib import Path
from database import engine
from admin import (
    UserAdmin, MatchAdmin, MessageAdmin, MissionAdmin, BlockAdmin, ReportAdmin, AdminAuth, OdoyewuAdmin,
    BadgeAdmin, UserProfileAdmin, ThemeAdmin, IcebreakerPromptAdmin, MoodCheckInAdmin,
    CompatibilityQuizAdmin, UserQuizResultAdmin, NudgeAdmin, EventAdmin, UserEventRegistrationAdmin,
    RelationshipTipAdmin, GuidedChatSessionAdmin, EmotionalSafetySettingAdmin
)

# Production imports
from config import settings
from logging_config import logger
import time

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"] if settings.RATE_LIMIT_ENABLED else []
)

app = FastAPI(
    title=settings.APP_NAME,
    description="Proximity-based, anonymous-first dating platform with premium gamification features",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None
)

logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} in {settings.ENVIRONMENT} mode")

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Create uploads directory
Path("uploads").mkdir(exist_ok=True)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    # Log response time
    process_time = time.time() - start_time
    logger.info(f"Response: {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response

# Security headers middleware
# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # --- START OF CSP FIX ---
    # The original "default-src 'self'" is replaced with a policy that allows
    # 'self' PLUS the external CDNs for Swagger UI and the required inline script hash.
    csp_policy = (
        "default-src 'self';"
        "script-src 'self' https://cdn.jsdelivr.net 'sha256-QOOQu4W1oxGqd2nbXbxiA1Di6OHQOLQD+o+G9oWL8YY=';" # Allow jsDelivr & specific inline script
        "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline';" # Allow jsDelivr & inline styles (for swagger)
        "img-src 'self' https://fastapi.tiangolo.com data:;" # Allow FastAPI favicon & data URIs
    )
    
    response.headers["Content-Security-Policy"] = csp_policy
    # --- END OF CSP FIX ---
    
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted host middleware (production only)
if settings.ENVIRONMENT == "production":
    allowed_hosts = settings.get_allowed_origins_list()
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# CORS - Secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,
)

logger.info(f"CORS configured for origins: {settings.get_allowed_origins_list()}")

# Custom exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request data", "errors": exc.errors() if settings.DEBUG else None}
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error" if settings.ENVIRONMENT == "production" else str(exc)}
    )

# Include routers
app.include_router(health.router)  # Health checks first
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(matches.router)
app.include_router(chat.router)
app.include_router(reveal.router)
app.include_router(missions.router)
app.include_router(safety.router)
app.include_router(photos.router)
app.include_router(hotspots.router)
app.include_router(notifications.router)

# Premium & Gamification Routers
app.include_router(themes.router)
app.include_router(icebreakers.router)
app.include_router(mood.router)
app.include_router(quizzes.router)
app.include_router(events.router)
app.include_router(tips.router)
app.include_router(guided_chat.router)

logger.info("All routers registered successfully")

# Admin Panel Setup
import os
authentication_backend = AdminAuth(secret_key=os.getenv("SECRET_KEY", "supersecretkey"))
admin = OdoyewuAdmin(app, engine, title="Odoyewu Admin", authentication_backend=authentication_backend, templates_dir="templates")

# Register all model views
admin.add_view(UserAdmin)
admin.add_view(MatchAdmin)
admin.add_view(MessageAdmin)
admin.add_view(MissionAdmin)
admin.add_view(BlockAdmin)
admin.add_view(ReportAdmin)

# Premium & Gamification Views
admin.add_view(BadgeAdmin)
admin.add_view(UserProfileAdmin)
admin.add_view(ThemeAdmin)
admin.add_view(IcebreakerPromptAdmin)
admin.add_view(MoodCheckInAdmin)
admin.add_view(CompatibilityQuizAdmin)
admin.add_view(UserQuizResultAdmin)
admin.add_view(NudgeAdmin)
admin.add_view(EventAdmin)
admin.add_view(UserEventRegistrationAdmin)
admin.add_view(RelationshipTipAdmin)
admin.add_view(GuidedChatSessionAdmin)
admin.add_view(EmotionalSafetySettingAdmin)

@app.get("/", tags=["Root"])
@limiter.limit("10/minute")
def read_root(request: Request):
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "health_check": "/health",
        "docs": "/docs" if settings.ENVIRONMENT != "production" else "disabled in production"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.APP_NAME} started successfully")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Rate limiting: {'enabled' if settings.RATE_LIMIT_ENABLED else 'disabled'}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"{settings.APP_NAME} shutting down")
