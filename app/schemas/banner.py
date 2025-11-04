from pydantic import BaseModel
from typing import Optional

class BannerBase(BaseModel):
    title: str
    image_url: str
    description: Optional[str] = None

class BannerCreate(BannerBase):
    pass

class BannerUpdate(BannerBase):
    pass

class BannerInDBBase(BannerBase):
    id: int
    class Config:
        from_attributes = True

class Banner(BannerInDBBase):
    pass
