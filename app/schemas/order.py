from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field

from app.models.order import OrderStatus, PaymentMethod, PaymentStatus


class OrderItemBase(BaseModel):
    product_id: uuid.UUID
    shop_id: uuid.UUID
    quantity: int = Field(..., ge=1)
    price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: uuid.UUID
    order_id: uuid.UUID
    product_name: str
    shop_name: str
    total_price: float
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    shipping_address: str
    billing_address: str
    payment_method: PaymentMethod
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]


class OrderStatusUpdateResponse(BaseModel):
    id: uuid.UUID
    status: OrderStatus
    comment: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class OrderResponse(OrderBase):
    id: uuid.UUID
    order_number: str
    status: OrderStatus
    total_amount: float
    payment_status: PaymentStatus
    tracking_number: Optional[str] = None
    shipping_company: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse] = []
    status_updates: List[OrderStatusUpdateResponse] = []
    
    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    tracking_number: Optional[str] = None
    shipping_company: Optional[str] = None
    notes: Optional[str] = None