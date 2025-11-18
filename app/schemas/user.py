from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, validator


class UserRole(str, Enum):
    CUSTOMER = "customer"
    LOGIST = "logist"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


# Base User schemas
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    profile_image: Optional[str] = None
    role: Optional[UserRole] = None
    shop_id: Optional[uuid.UUID] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    password_confirm: str
    
    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class AdminUserCreate(UserCreate):
    """Schema for admin creating users with specific roles"""
    is_superuser: Optional[bool] = False
    is_active: Optional[bool] = True


class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8)
    profile_image_b64: Optional[str] = None

    @validator('profile_image_b64')
    def validate_base64_image(cls, v):
        if v is not None:
            try:
                # Check if it's a valid base64 string
                if not v.startswith('data:image/'):
                    raise ValueError('Invalid base64 image format. Must start with data:image/')
                # Extract the actual base64 string after the comma
                base64_data = v.split(',')[1]
                import base64
                base64.b64decode(base64_data)
            except Exception as e:
                raise ValueError('Invalid base64 image format')
        return v


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


class LogistUserResponse(UserResponse):
    """User response with additional shop information for logists"""
    shop_name: Optional[str] = None
    
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


# Additional user management schemas
class UserRoleUpdate(BaseModel):
    """Schema for updating a user's role"""
    role: UserRole


class UserActivationUpdate(BaseModel):
    """Schema for activating/deactivating a user"""
    is_active: bool


class UserFilter(BaseModel):
    """Schema for filtering users"""
    search_term: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    shop_id: Optional[uuid.UUID] = None
    skip: int = 0
    limit: int = 100
    sort_by: str = "created_at"
    sort_desc: bool = True


class UserCount(BaseModel):
    """Schema for user count response"""
    count: int


class BulkUserIds(BaseModel):
    """Schema for bulk operations on users"""
    user_ids: List[uuid.UUID]



class ProfileImageUpdate(BaseModel):
    """Schema for updating profile image"""
    profile_image: str = Field(..., description="The profile image URL or base64 string")


class BulkOperationResponse(BaseModel):
    """Schema for bulk operation response"""
    results: Dict[str, bool]
    success_count: int
    failure_count: int