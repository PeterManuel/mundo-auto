from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel

from app.models.order import OrderStatus, PaymentMethod, PaymentStatus


class InvoiceItemData(BaseModel):
    """Invoice item data"""
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    shop_name: str
    sku: Optional[str] = None
    oe_number: Optional[str] = None
    brand: Optional[str] = None
    
    class Config:
        from_attributes = True


class InvoiceCustomerData(BaseModel):
    """Invoice customer data"""
    customer_id: uuid.UUID
    name: str
    email: str
    phone_number: Optional[str] = None
    
    class Config:
        from_attributes = True


class InvoiceShopData(BaseModel):
    """Invoice shop data"""
    shop_id: uuid.UUID
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    logo: Optional[str] = None
    
    class Config:
        from_attributes = True


class InvoiceData(BaseModel):
    """Complete invoice data for frontend consumption"""
    # Order information
    order_id: uuid.UUID
    order_number: str
    invoice_number: str
    invoice_date: datetime
    due_date: Optional[datetime] = None
    
    # Order details
    order_date: datetime
    order_status: OrderStatus
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    
    # Customer information
    customer: InvoiceCustomerData
    
    # Shop information  
    shop: InvoiceShopData
    
    # Addresses
    billing_address: str
    shipping_address: str
    
    # Items
    items: List[InvoiceItemData]
    
    # Financial totals
    subtotal: float
    shipping_cost: float
    tax_amount: float
    tax_rate: float
    total_amount: float
    
    # Additional info
    notes: Optional[str] = None
    tracking_number: Optional[str] = None
    shipping_company: Optional[str] = None
    
    class Config:
        from_attributes = True