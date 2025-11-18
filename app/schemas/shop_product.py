from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from pydantic import BaseModel, Field


# ShopProduct schemas
class ShopProductBase(BaseModel):
    shop_id: uuid.UUID
    name: str
    description: Optional[str] = None
    technical_details: Optional[str] = None
    price: float = Field(..., gt=0)
    sale_price: Optional[float] = None
    sku: Optional[str] = None
    oe_number: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    manufacturer_year: Optional[int] = None
    compatible_vehicles: Optional[List[str]] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    image: Optional[str] = None  # Base64 encoded image
    is_featured: bool = False
    is_on_sale: bool = False
    stock_quantity: int = 0


class ShopProductCreate(ShopProductBase):
    slug: Optional[str] = None
    category_ids: List[uuid.UUID] = []


class ShopProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technical_details: Optional[str] = None
    price: Optional[float] = None
    sale_price: Optional[float] = None
    sku: Optional[str] = None
    oe_number: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    manufacturer_year: Optional[int] = None
    compatible_vehicles: Optional[List[str]] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    image: Optional[str] = None
    is_featured: Optional[bool] = None
    is_on_sale: Optional[bool] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None
    category_ids: Optional[List[uuid.UUID]] = None


class ShopProductResponse(ShopProductBase):
    id: uuid.UUID
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    categories: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True


class ShopProductFullResponse(ShopProductResponse):
    """
    Full response with shop details
    """
    shop_name: str
    
    class Config:
        from_attributes = True