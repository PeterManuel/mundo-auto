import uuid
from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class VehicleModel(Base):
    """
    VehicleModel model representing vehicle models that belong to a specific vehicle
    """
    __tablename__ = "vehicle_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="models")
    shop_products = relationship("ShopProduct", secondary="vehicle_model_shop_product", back_populates="vehicle_models")
    
    def __repr__(self):
        return f"<VehicleModel {self.name} for Vehicle {self.vehicle_id}>"