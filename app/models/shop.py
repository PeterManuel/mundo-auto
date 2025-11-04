import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Shop(Base):
    """
    Shop model representing a store/shop in the multi-shop system
    """
    __tablename__ = "shops"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    logo = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Geolocation for the shop
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Social media links
    website = Column(String(255), nullable=True)
    facebook = Column(String(255), nullable=True)
    instagram = Column(String(255), nullable=True)
    twitter = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    shop_products = relationship("ShopProduct", back_populates="shop", cascade="all, delete-orphan")
    users = relationship("User", back_populates="shop")  # Logists associated with this shop
    
    def __repr__(self):
        return f"<Shop {self.name}>"