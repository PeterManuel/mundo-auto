from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Dict, Optional, Union
from dotenv import load_dotenv
import os

# Load the environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "MundoAuto"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your_super_secret_key_here_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database - These will be loaded from environment variables
    DATABASE_URL: Optional[str] = None
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "mundo_auto"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URI(self) -> str:
        # If DATABASE_URL is provided, use it directly
        if self.DATABASE_URL:
            return self.DATABASE_URL
        # Otherwise construct from components
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Social Login
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    FACEBOOK_CLIENT_ID: Optional[str] = None
    FACEBOOK_CLIENT_SECRET: Optional[str] = None

    # Uploads
    UPLOAD_DIRECTORY: str = "uploads"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Emails
    EMAILS_ENABLED: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )


# Initialize settings with environment variables
settings = Settings(
    PROJECT_NAME=os.getenv("PROJECT_NAME", "MundoAuto"),
    PROJECT_VERSION=os.getenv("PROJECT_VERSION", "0.1.0"),
    SECRET_KEY=os.getenv("SECRET_KEY", "your_super_secret_key_here_change_in_production"),
    POSTGRES_SERVER=os.getenv("POSTGRES_SERVER", "localhost"),
    POSTGRES_USER=os.getenv("POSTGRES_USER", "postgres"),
    POSTGRES_PASSWORD=os.getenv("POSTGRES_PASSWORD", "postgres"),
    POSTGRES_DB=os.getenv("POSTGRES_DB", "mundo_auto"),
    POSTGRES_PORT=int(os.getenv("POSTGRES_PORT", "5432")),
    DATABASE_URL=os.getenv("DATABASE_URL"),
)