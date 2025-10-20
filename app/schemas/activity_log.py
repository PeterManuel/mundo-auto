from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

from pydantic import BaseModel, Field


# Base ActivityLog Schema
class ActivityLogBase(BaseModel):
    endpoint: str
    method: str
    path: str
    status_code: Optional[str] = None
    request_body: Optional[str] = None
    response_body: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[str] = None


class ActivityLogCreate(ActivityLogBase):
    user_id: Optional[uuid.UUID] = None


class ActivityLogUpdate(BaseModel):
    status_code: Optional[str] = None
    response_body: Optional[str] = None
    processing_time_ms: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None


class ActivityLogResponse(ActivityLogBase):
    id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ActivityLogFilter(BaseModel):
    user_id: Optional[uuid.UUID] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    path: Optional[str] = None
    status_code: Optional[str] = None
    ip_address: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None