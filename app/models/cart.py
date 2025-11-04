from datetime import datetime
import uuid
from typing import List, Optional

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    shop_product_id = Column(UUID(as_uuid=True), ForeignKey("shop_products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="cart_items")
    shop_product = relationship("ShopProduct")

    @property
    def total_price(self):
        # Use shop_product price if available
        price = self.shop_product.sale_price if self.shop_product.sale_price else self.shop_product.price
        if price is None:
            # Fallback to product price
            price = self.shop_product.product.sale_price if self.shop_product.product.sale_price else self.shop_product.product.price
        return price * self.quantity