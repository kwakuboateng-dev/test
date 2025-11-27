"""
Production-ready configuration management with validation.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Odoyewu API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY", min_length=32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DB_POOL_SIZE: int = Field(default=20, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=10, env="DB_MAX_OVERFLOW")
    
    # CORS
    ALLOWED_ORIGINS: str = Field(default="", env="ALLOWED_ORIGINS")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # File Upload
    MAX_UPLOAD_SIZE: int = Field(default=5242880, env="MAX_UPLOAD_SIZE")  # 5MB
    ALLOWED_EXTENSIONS: str = Field(default="jpg,jpeg,png,gif", env="ALLOWED_EXTENSIONS")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Email (for notifications)
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: Optional[int] = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        if values.get("ENVIRONMENT") == "production":
            if v == "your-secret-key-here-change-in-production" or len(v) < 32:
                raise ValueError("SECRET_KEY must be strong in production (min 32 chars)")
        return v
    
    @validator("ALLOWED_ORIGINS")
    def validate_cors(cls, v, values):
        if values.get("ENVIRONMENT") == "production" and (not v or v == "*"):
            raise ValueError("ALLOWED_ORIGINS must be set in production (no wildcards)")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()
    
    def get_allowed_origins_list(self):
        """Parse ALLOWED_ORIGINS into a list"""
        if not self.ALLOWED_ORIGINS:
            return ["http://localhost:8081", "http://localhost:8000", "http://localhost:19006"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    def get_allowed_extensions_list(self):
        """Parse ALLOWED_EXTENSIONS into a list"""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
try:
    settings = Settings()
except Exception as e:
    print(f"❌ Configuration Error: {e}")
    print("Please check your .env file and ensure all required variables are set.")
    raise

# Validate production settings
if settings.ENVIRONMENT == "production":
    print("✅ Production configuration validated")
    if settings.DEBUG:
        print("⚠️  WARNING: DEBUG is enabled in production!")
