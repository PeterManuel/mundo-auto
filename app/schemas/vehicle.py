from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid

from pydantic import BaseModel, Field


# VehicleModel schemas
class VehicleModelBase(BaseModel):
    name: str
    description: Optional[str] = None
    vehicle_id: uuid.UUID


class VehicleModelCreate(VehicleModelBase):
    pass


class VehicleModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    vehicle_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None


class VehicleModelResponse(VehicleModelBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Vehicle schemas
class VehicleBase(BaseModel):
    brand: str
    manufacturer_year: Optional[int] = None
    description: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    brand: Optional[str] = None
    manufacturer_year: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class VehicleResponse(VehicleBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    models: List[Dict[str, Any]] = []  # Include models list in response
    
    class Config:
        from_attributes = True


class VehicleWithProducts(VehicleResponse):
    """
    Vehicle response with associated shop products
    """
    shop_products: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True


# ShopProductImage schemas
class ShopProductImageBase(BaseModel):
    image_data: str
    alt_text: Optional[str] = None
    is_primary: bool = False
    display_order: int = 0


class ShopProductImageCreate(ShopProductImageBase):
    pass


class ShopProductImageUpdate(BaseModel):
    image_data: Optional[str] = None
    alt_text: Optional[str] = None
    is_primary: Optional[bool] = None
    display_order: Optional[int] = None


class ShopProductImageResponse(ShopProductImageBase):
    id: uuid.UUID
    shop_product_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True