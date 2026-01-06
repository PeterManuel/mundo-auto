import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class ShopProductImage(Base):
    """
    ShopProductImage model representing images for shop products
    """
    __tablename__ = "shop_product_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shop_product_id = Column(UUID(as_uuid=True), ForeignKey("shop_products.id", ondelete="CASCADE"), nullable=False)
    image_data = Column(Text, nullable=False)  # Base64 encoded image
    alt_text = Column(String, nullable=True)  # Alt text for accessibility
    is_primary = Column(Boolean, default=False, nullable=False)  # One primary image per product
    display_order = Column(Integer, default=0, nullable=False)  # Order for display
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    shop_product = relationship("ShopProduct", back_populates="images")
    
    def __repr__(self):
        return f"<ShopProductImage {self.id} for product {self.shop_product_id}>"