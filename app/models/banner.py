from sqlalchemy import Column, Integer, String
from app.db.base_class import Base

class Banner(Base):
    __tablename__ = "banners"
    __table_args__ = ({'extend_existing': True},)
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    description = Column(String, nullable=True)
