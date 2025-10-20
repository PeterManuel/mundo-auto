from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


class CartItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(1, ge=1)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemResponse(CartItemBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    product_name: str
    product_price: float
    product_image: Optional[str] = None
    total_price: float
    
    class Config:
        from_attributes = True


class CartSummaryResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    subtotal: float