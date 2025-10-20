from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, EmailStr, Field, validator


# Base User schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    profile_image: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    google_id: Optional[str] = None
    facebook_id: Optional[str] = None
    
    class Config:
        from_attributes = True


# Login History schema
class LoginHistoryBase(BaseModel):
    login_timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class LoginHistoryResponse(LoginHistoryBase):
    id: uuid.UUID
    user_id: uuid.UUID
    
    class Config:
        from_attributes = True


# OAuth schemas
class GoogleAuthRequest(BaseModel):
    code: str


class GoogleAuthResponse(BaseModel):
    access_token: str
    token_type: str