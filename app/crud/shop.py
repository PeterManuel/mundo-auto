from typing import List, Optional
import uuid

from slugify import slugify
from sqlalchemy.orm import Session

from app.models.shop import Shop
from app.schemas.shop import ShopCreate, ShopUpdate


def get_shop(db: Session, shop_id: uuid.UUID) -> Optional[Shop]:
    """Get shop by ID"""
    return db.query(Shop).filter(Shop.id == shop_id).first()


def get_shop_by_slug(db: Session, slug: str) -> Optional[Shop]:
    """Get shop by slug"""
    return db.query(Shop).filter(Shop.slug == slug).first()


def get_shops(db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None) -> List[Shop]:
    """
    Get all shops with optional filtering by active status
    """
    query = db.query(Shop)
    
    if is_active is not None:
        query = query.filter(Shop.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


def create_shop(db: Session, shop: ShopCreate) -> Shop:
    """
    Create a new shop
    """
    # Generate slug if not provided
    if not shop.slug:
        shop.slug = slugify(shop.name)
    
    # Check if slug exists
    existing_shop = get_shop_by_slug(db, shop.slug)
    if existing_shop:
        # If slug already exists, append a unique identifier
        shop.slug = f"{shop.slug}-{uuid.uuid4().hex[:8]}"
    
    # Create shop object
    # Convert HttpUrl to string if it exists
    website = str(shop.website) if shop.website else None
    
    db_shop = Shop(
        name=shop.name,
        slug=shop.slug,
        description=shop.description,
        address=shop.address,
        phone=shop.phone,
        email=shop.email,
        logo=shop.logo,
        latitude=shop.latitude,
        longitude=shop.longitude,
        website=website,
        facebook=shop.facebook,
        instagram=shop.instagram,
        twitter=shop.twitter,
    )
    
    db.add(db_shop)
    db.commit()
    db.refresh(db_shop)
    return db_shop


def update_shop(db: Session, shop_id: uuid.UUID, shop: ShopUpdate) -> Optional[Shop]:
    """
    Update a shop
    """
    db_shop = get_shop(db, shop_id)
    if not db_shop:
        return None
    
    # Update shop attributes
    update_data = shop.dict(exclude_unset=True)
    
    # Handle slug separately if name is changing
    if "name" in update_data and update_data["name"] != db_shop.name and "slug" not in update_data:
        new_slug = slugify(update_data["name"])
        # Check if slug exists
        existing_shop = get_shop_by_slug(db, new_slug)
        if existing_shop and existing_shop.id != shop_id:
            # If slug already exists for another shop, append a unique identifier
            new_slug = f"{new_slug}-{uuid.uuid4().hex[:8]}"
        update_data["slug"] = new_slug
    
    # Convert HttpUrl to string if it exists
    if "website" in update_data and update_data["website"]:
        update_data["website"] = str(update_data["website"])
    
    for key, value in update_data.items():
        setattr(db_shop, key, value)
    
    db.add(db_shop)
    db.commit()
    db.refresh(db_shop)
    return db_shop


def delete_shop(db: Session, shop_id: uuid.UUID) -> bool:
    """
    Delete a shop
    """
    db_shop = get_shop(db, shop_id)
    if not db_shop:
        return False
    
    db.delete(db_shop)
    db.commit()
    return True