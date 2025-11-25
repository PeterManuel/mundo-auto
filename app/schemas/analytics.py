from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class BestSellingProduct(BaseModel):
    """Schema for best-selling product analytics"""
    id: uuid.UUID
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    oe_number: Optional[str] = None
    price: float
    total_quantity_sold: int
    total_revenue: float
    shop_name: str
    
    class Config:
        from_attributes = True


class MostActiveCustomer(BaseModel):
    """Schema for most active customer analytics"""
    id: uuid.UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    total_orders: int
    total_spent: float
    last_order_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LowStockProduct(BaseModel):
    """Schema for low stock product analytics"""
    id: uuid.UUID
    name: str
    brand: Optional[str] = None
    model: Optional[str] = None
    oe_number: Optional[str] = None
    price: float
    current_stock: int
    shop_name: str
    is_active: bool
    
    class Config:
        from_attributes = True


class AnalyticsFilter(BaseModel):
    """Filter schema for analytics endpoints"""
    days: Optional[int] = Field(default=30, description="Number of days to look back for analytics")
    limit: Optional[int] = Field(default=10, description="Maximum number of results to return")
    min_stock_threshold: Optional[int] = Field(default=5, description="Threshold for low stock products")