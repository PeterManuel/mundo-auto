from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field

from app.models.order import OrderStatus, PaymentMethod, PaymentStatus


class OrderItemBase(BaseModel):
    shop_product_id: uuid.UUID
    quantity: int = Field(..., ge=1)
    price: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: uuid.UUID
    order_id: uuid.UUID
    product_name: str
    shop_name: str
    
    @property
    def total_price(self) -> float:
        return self.price * self.quantity
    
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


class OrdersCreatedResponse(BaseModel):
    """Response for orders created from cart (multiple orders per shop)"""
    orders: List[OrderResponse]
    total_orders: int
    message: str
    
    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    tracking_number: Optional[str] = None
    shipping_company: Optional[str] = None
    notes: Optional[str] = None


class OrderFilter(BaseModel):
    """Schema for filtering shop orders"""
    status: Optional[OrderStatus] = None
    customer_id: Optional[uuid.UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 100


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status with comment"""
    status: OrderStatus
    comment: Optional[str] = None


class ShopOrderSummary(BaseModel):
    """Summary of orders for a shop"""
    total_orders: int
    pending_orders: int
    processing_orders: int
    shipped_orders: int
    delivered_orders: int
    cancelled_orders: int
    total_revenue: float
    
    class Config:
        from_attributes = True


class CustomerOrderHistory(BaseModel):
    """Customer order history for a specific shop"""
    customer_id: uuid.UUID
    customer_name: str
    customer_email: str
    total_orders: int
    total_spent: float
    last_order_date: Optional[datetime] = None
    orders: List[OrderResponse] = []
    
    class Config:
        from_attributes = True