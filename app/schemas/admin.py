from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from pydantic import BaseModel


class BannerBase(BaseModel):
    title: str
    subtitle: Optional[str] = None
    image_url: str
    link_url: Optional[str] = None
    position: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BannerCreate(BannerBase):
    pass


class BannerUpdate(BannerBase):
    title: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class BannerResponse(BannerBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SystemSettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SystemSettingUpdate(BaseModel):
    value: str
    description: Optional[str] = None


class SystemSettingResponse(SystemSettingBase):
    id: uuid.UUID
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReportBase(BaseModel):
    name: str
    description: Optional[str] = None
    report_type: str
    parameters: Optional[Dict[str, Any]] = None


class ReportCreate(ReportBase):
    pass


class ReportResponse(ReportBase):
    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    total_sales: float
    total_orders: int
    pending_orders: int
    total_products: int
    low_stock_products: int
    active_users: int
    top_selling_products: List[Dict[str, Any]]
    recent_orders: List[Dict[str, Any]]