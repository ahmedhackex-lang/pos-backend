"""
Application configuration using Pydantic Settings
Reads from environment variables
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Grocery POS Cloud Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database (Supabase PostgreSQL)
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 8
    
    # CORS
    ALLOWED_ORIGINS: str = "*"  # Change in production
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()