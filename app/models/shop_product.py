import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, Float, Boolean, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class ShopProduct(Base):
    """
    ShopProduct model representing a product in a specific shop with shop-specific details like stock and price
    """
    __tablename__ = "shop_products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    
    # Shop-specific product details
    stock_quantity = Column(Integer, default=0, nullable=False)
    price = Column(Float, nullable=True)  # Shop-specific price, if NULL use product's default price
    sale_price = Column(Float, nullable=True)  # Shop-specific sale price
    sku = Column(String(100), nullable=True)  # Shop-specific SKU
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    shop = relationship("Shop", back_populates="shop_products")
    product = relationship("Product", back_populates="shop_products")
    
    def __repr__(self):
        return f"<ShopProduct {self.product_id} in shop {self.shop_id}>"