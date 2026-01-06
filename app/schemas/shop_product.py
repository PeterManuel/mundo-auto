from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from pydantic import BaseModel, Field

from app.schemas.vehicle import ShopProductImageResponse


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
    # Removed image field - now handled by ShopProductImage model
    is_featured: bool = False
    is_on_sale: bool = False
    stock_quantity: int = 0


class ShopProductCreate(ShopProductBase):
    slug: Optional[str] = None
    category_ids: List[uuid.UUID] = []
    vehicle_ids: List[uuid.UUID] = []  # Required: at least one vehicle
    images: List[Dict[str, Any]] = []  # List of image data


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
    # Removed image field - now handled by ShopProductImage model
    is_featured: Optional[bool] = None
    is_on_sale: Optional[bool] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None
    category_ids: Optional[List[uuid.UUID]] = None
    vehicle_ids: Optional[List[uuid.UUID]] = None
    images: Optional[List[Dict[str, Any]]] = None  # List of image data


class ShopProductResponse(ShopProductBase):
    id: uuid.UUID
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    categories: List[Dict[str, Any]] = []
    vehicles: List[Dict[str, Any]] = []
    images: List[ShopProductImageResponse] = []
    
    class Config:
        from_attributes = True


class ShopProductFullResponse(ShopProductResponse):
    """
    Full response with shop details
    """
    shop_name: str
    
    class Config:
        from_attributes = True