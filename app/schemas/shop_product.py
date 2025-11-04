from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


# ShopProduct schemas
class ShopProductBase(BaseModel):
    shop_id: uuid.UUID
    product_id: uuid.UUID
    stock_quantity: int = 0
    price: Optional[float] = None  # If not provided, use the product's default price
    sale_price: Optional[float] = None
    sku: Optional[str] = None


class ShopProductCreate(ShopProductBase):
    pass


class ShopProductUpdate(BaseModel):
    stock_quantity: Optional[int] = None
    price: Optional[float] = None
    sale_price: Optional[float] = None
    sku: Optional[str] = None
    is_active: Optional[bool] = None


class ShopProductResponse(ShopProductBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Include basic product information
    product_name: str
    product_description: Optional[str] = None
    model: Optional[str] = None
    manufacturer_year: Optional[int] = None
    
    class Config:
        from_attributes = True


class ShopProductFullResponse(ShopProductResponse):
    """
    Full response with product and shop details
    """
    shop_name: str
    product_images: List[str] = []
    product_categories: List[str] = []
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    manufacturer_year: Optional[int] = None
    
    class Config:
        from_attributes = True