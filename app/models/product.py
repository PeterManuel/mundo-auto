from datetime import datetime
import uuid
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Table, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

# Product-Category many-to-many relationship
product_category = Table(
    "product_category",
    Base.metadata,
    Column("product_id", UUID(as_uuid=True), ForeignKey("products.id"), primary_key=True),
    Column("category_id", UUID(as_uuid=True), ForeignKey("categories.id"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    image = Column(Text, nullable=True)  # Store base64 image string
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referential relationship for hierarchical categories
    subcategories = relationship("Category", backref="parent", remote_side=[id])
    
    # Many-to-many relationship with products
    products = relationship("Product", secondary=product_category, back_populates="categories")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    technical_details = Column(Text, nullable=True)
    price = Column(Float, nullable=False)  # Base/reference price
    sale_price = Column(Float, nullable=True)  # Base/reference sale price
    sku = Column(String, nullable=True)  # Base/reference SKU (no longer unique as each shop may have its own)
    oe_number = Column(String, nullable=True, index=True)  # Original Equipment number
    # stock_quantity moved to ShopProduct
    brand = Column(String, nullable=True, index=True)
    manufacturer = Column(String, nullable=True)
    model = Column(String, nullable=True, index=True)  # Vehicle model
    manufacturer_year = Column(Integer, nullable=True)  # Vehicle manufacturer year
    compatible_vehicles = Column(ARRAY(String), nullable=True)  # Array of vehicle compatibility
    weight = Column(Float, nullable=True)  # Weight in kg
    dimensions = Column(String, nullable=True)  # Format: "LxWxH" in cm
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_on_sale = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    categories = relationship("Category", secondary=product_category, back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    shop_products = relationship("ShopProduct", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("ProductReview", back_populates="product", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="product")


class ProductImage(Base):
    __tablename__ = "product_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    image_data = Column(Text, nullable=False)  # Store base64 image string
    alt_text = Column(String, nullable=True)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="images")


class ProductReview(Base):
    __tablename__ = "product_reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="reviews")
    user = relationship("User")


class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlist_items")