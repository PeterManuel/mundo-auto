from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Dict, Optional, Union


class Settings(BaseSettings):
    PROJECT_NAME: str = "MundoAuto"
    PROJECT_VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "supersecretkey"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    POSTGRES_SERVER: str = "dpg-d3qulr7diees73alaugg-a.oregon-postgres.render.com"
    POSTGRES_USER: str = "mundo_auto_user"
    POSTGRES_PASSWORD: str = "TGfVWQNQitGvvFJbMsS3zZIIcwb2I65B"
    POSTGRES_DB: str = "mundo_auto"
    POSTGRES_PORT: str = "5432"
    
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
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', case_sensitive=True)
    
    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


settings = Settings()