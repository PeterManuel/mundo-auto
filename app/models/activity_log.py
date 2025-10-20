from datetime import datetime
import json
import uuid
from typing import Dict, Optional, Any

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # User information (if authenticated)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Request information
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    path = Column(String, nullable=False)
    status_code = Column(String, nullable=True)
    
    # Request details
    request_body = Column(Text, nullable=True)  # JSON serialized
    response_body = Column(Text, nullable=True)  # JSON serialized (truncated if large)
    
    # Device information
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    device_type = Column(String, nullable=True)
    browser = Column(String, nullable=True)
    os = Column(String, nullable=True)
    
    # Custom data
    extra_data = Column(JSON, nullable=True)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    processing_time_ms = Column(String, nullable=True)  # Time taken to process request
    
    # Relationships
    user = relationship("User", backref="activity_logs")

    def __repr__(self):
        return f"<ActivityLog id={self.id} endpoint={self.endpoint} method={self.method}>"