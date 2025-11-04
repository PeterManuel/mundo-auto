
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.banner import Banner, BannerCreate, BannerUpdate
from app.crud.banner import get_banners, get_banner, create_banner, update_banner, delete_banner
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[Banner])
def read_banners(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_banners(db, skip=skip, limit=limit)

@router.get("/{banner_id}", response_model=Banner)
def read_banner(banner_id: int, db: Session = Depends(get_db)):
    db_banner = get_banner(db, banner_id)
    if not db_banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return db_banner

@router.post("/", response_model=Banner)
def create_new_banner(banner: BannerCreate, db: Session = Depends(get_db)):
    return create_banner(db, banner)

@router.put("/{banner_id}", response_model=Banner)
def update_existing_banner(banner_id: int, banner: BannerUpdate, db: Session = Depends(get_db)):
    db_banner = update_banner(db, banner_id, banner)
    if not db_banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return db_banner

@router.delete("/{banner_id}", response_model=Banner)
def delete_existing_banner(banner_id: int, db: Session = Depends(get_db)):
    db_banner = delete_banner(db, banner_id)
    if not db_banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return db_banner
