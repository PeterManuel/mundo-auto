from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, EmailStr, Field, HttpUrl


# Shop schemas
class ShopBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    logo: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    website: Optional[HttpUrl] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None


class ShopCreate(ShopBase):
    slug: Optional[str] = None


class ShopUpdate(ShopBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class ShopResponse(ShopBase):
    id: uuid.UUID
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True