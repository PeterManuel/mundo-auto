from datetime import datetime
from typing import List, Optional
import uuid

from pydantic import BaseModel, Field


# Category schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    # parent_id is now ignored in create operations, but kept for compatibility
    parent_id: Optional[uuid.UUID] = None
    image: Optional[str] = None


class CategoryCreate(CategoryBase):
    slug: Optional[str] = None


class CategoryUpdate(CategoryBase):
    name: Optional[str] = None
    slug: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: uuid.UUID
    slug: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class CategoryWithSubcategories(CategoryResponse):
    subcategories: List["CategoryResponse"] = []
    
    class Config:
        from_attributes = True


# Product schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    technical_details: Optional[str] = None
    price: float = Field(..., gt=0)
    sale_price: Optional[float] = None
    sku: Optional[str] = None
    oe_number: Optional[str] = None  # Original Equipment number
    stock_quantity: int = 0
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    compatible_vehicles: Optional[List[str]] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    is_featured: bool = False
    is_on_sale: bool = False


class ProductCreate(ProductBase):
    slug: Optional[str] = None
    category_ids: List[uuid.UUID]


class ProductUpdate(ProductBase):
    name: Optional[str] = None
    price: Optional[float] = None
    category_ids: Optional[List[uuid.UUID]] = None


class ProductImageResponse(BaseModel):
    id: uuid.UUID
    image_url: str
    alt_text: Optional[str] = None
    is_primary: bool
    
    class Config:
        from_attributes = True


class ProductResponse(ProductBase):
    id: uuid.UUID
    slug: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    images: List[ProductImageResponse] = []
    categories: List[CategoryResponse] = []
    
    class Config:
        from_attributes = True


# Product Review schemas
class ProductReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ProductReviewCreate(ProductReviewBase):
    product_id: uuid.UUID


class ProductReviewResponse(ProductReviewBase):
    id: uuid.UUID
    product_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    
    class Config:
        from_attributes = True