from sqlalchemy.orm import Session
from app.models.banner import Banner
from app.schemas.banner import BannerCreate, BannerUpdate


def get_banner(db: Session, banner_id: int):
    return db.query(Banner).filter(Banner.id == banner_id).first()


def get_banners(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Banner).offset(skip).limit(limit).all()


def create_banner(db: Session, banner: BannerCreate):
    db_banner = Banner(**banner.dict())
    db.add(db_banner)
    db.commit()
    db.refresh(db_banner)
    return db_banner


def update_banner(db: Session, banner_id: int, banner: BannerUpdate):
    db_banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if db_banner:
        for key, value in banner.dict(exclude_unset=True).items():
            setattr(db_banner, key, value)
        db.commit()
        db.refresh(db_banner)
    return db_banner


def delete_banner(db: Session, banner_id: int):
    db_banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if db_banner:
        db.delete(db_banner)
        db.commit()
    return db_banner
