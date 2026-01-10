import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, Float, Boolean, DateTime, String, Text, Table
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from app.db.session import Base

# ShopProduct-Category many-to-many relationship
shop_product_category = Table(
    "shop_product_category",
    Base.metadata,
    Column("shop_product_id", UUID(as_uuid=True), ForeignKey("shop_products.id"), primary_key=True),
    Column("category_id", UUID(as_uuid=True), ForeignKey("categories.id"), primary_key=True),
)

# VehicleModel-ShopProduct many-to-many relationship
vehicle_model_shop_product = Table(
    "vehicle_model_shop_product",
    Base.metadata,
    Column("vehicle_model_id", UUID(as_uuid=True), ForeignKey("vehicle_models.id"), primary_key=True),
    Column("shop_product_id", UUID(as_uuid=True), ForeignKey("shop_products.id"), primary_key=True),
)


class ShopProduct(Base):
    """
    ShopProduct model representing an autonomous product in a specific shop with all product details
    """
    __tablename__ = "shop_products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    
    # Product information (previously from Product model)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, nullable=False, index=True)  # Not unique anymore since different shops can have same product
    description = Column(Text, nullable=True)
    technical_details = Column(Text, nullable=True)
    price = Column(Float, nullable=False)  # Required price for the shop
    sale_price = Column(Float, nullable=True)  # Sale price
    sku = Column(String(100), nullable=True)  # Shop-specific SKU
    oe_number = Column(String, nullable=True, index=True)  # Original Equipment number
    brand = Column(String, nullable=True, index=True)
    manufacturer = Column(String, nullable=True)
    model = Column(String, nullable=True, index=True)  # Vehicle model
    manufacturer_year = Column(Integer, nullable=True)  # Vehicle manufacturer year
    compatible_vehicles = Column(ARRAY(String), nullable=True)  # Array of vehicle compatibility
    weight = Column(Float, nullable=True)  # Weight in kg
    dimensions = Column(String, nullable=True)  # Format: "LxWxH" in cm
    # Removed image field - now handled by ShopProductImage model
    is_featured = Column(Boolean, default=False)
    is_on_sale = Column(Boolean, default=False)
    
    # Shop-specific details
    stock_quantity = Column(Integer, default=0, nullable=False)
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    shop = relationship("Shop", back_populates="shop_products")
    categories = relationship("Category", secondary=shop_product_category, back_populates="shop_products")
    vehicle_models = relationship("VehicleModel", secondary=vehicle_model_shop_product, back_populates="shop_products")
    images = relationship("ShopProductImage", back_populates="shop_product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="shop_product")
    
    def __repr__(self):
        return f"<ShopProduct {self.name} in shop {self.shop_id}>"