from typing import List, Optional
import uuid
import os

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.shop_product_image import ShopProductImage
from app.schemas.shop_product import ShopProductImageCreate, ShopProductImageUpdate


def get_shop_product_image(db: Session, image_id: uuid.UUID) -> Optional[ShopProductImage]:
    """Get shop product image by ID"""
    return db.query(ShopProductImage).filter(ShopProductImage.id == image_id).first()


def get_shop_product_images(
    db: Session, 
    shop_product_id: uuid.UUID,
    is_active: Optional[bool] = None
) -> List[ShopProductImage]:
    """Get all images for a shop product"""
    query = db.query(ShopProductImage).filter(ShopProductImage.shop_product_id == shop_product_id)
    
    if is_active is not None:
        query = query.filter(ShopProductImage.is_active == is_active)
    
    return query.order_by(ShopProductImage.display_order, ShopProductImage.created_at).all()


def get_primary_image(db: Session, shop_product_id: uuid.UUID) -> Optional[ShopProductImage]:
    """Get the primary image for a shop product"""
    return db.query(ShopProductImage).filter(
        and_(
            ShopProductImage.shop_product_id == shop_product_id,
            ShopProductImage.is_primary == True,
            ShopProductImage.is_active == True
        )
    ).first()


def create_shop_product_image(db: Session, image: ShopProductImageCreate) -> ShopProductImage:
    """Create a new shop product image"""
    # If this is set as primary, ensure no other images are primary for this product
    if image.is_primary:
        db.query(ShopProductImage).filter(
            ShopProductImage.shop_product_id == image.shop_product_id
        ).update({"is_primary": False})
    
    # If no display_order is provided, set it to the next available order
    if image.display_order is None:
        max_order = db.query(
            ShopProductImage.display_order
        ).filter(
            ShopProductImage.shop_product_id == image.shop_product_id
        ).order_by(ShopProductImage.display_order.desc()).first()
        
        image.display_order = (max_order[0] + 1) if max_order and max_order[0] else 1
    
    db_image = ShopProductImage(**image.dict())
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def update_shop_product_image(
    db: Session, 
    image_id: uuid.UUID, 
    image: ShopProductImageUpdate
) -> Optional[ShopProductImage]:
    """Update a shop product image"""
    db_image = get_shop_product_image(db, image_id)
    if not db_image:
        return None
    
    update_data = image.dict(exclude_unset=True)
    
    # If setting as primary, ensure no other images are primary for this product
    if update_data.get("is_primary"):
        db.query(ShopProductImage).filter(
            and_(
                ShopProductImage.shop_product_id == db_image.shop_product_id,
                ShopProductImage.id != image_id
            )
        ).update({"is_primary": False})
    
    for field, value in update_data.items():
        setattr(db_image, field, value)
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def delete_shop_product_image(db: Session, image_id: uuid.UUID) -> bool:
    """Delete a shop product image"""
    db_image = get_shop_product_image(db, image_id)
    if not db_image:
        return False
    
    # Store file path for deletion
    file_path = db_image.image_url
    
    # If this was the primary image, set another image as primary
    if db_image.is_primary:
        next_image = db.query(ShopProductImage).filter(
            and_(
                ShopProductImage.shop_product_id == db_image.shop_product_id,
                ShopProductImage.id != image_id,
                ShopProductImage.is_active == True
            )
        ).order_by(ShopProductImage.display_order).first()
        
        if next_image:
            next_image.is_primary = True
            db.add(next_image)
    
    db.delete(db_image)
    db.commit()
    
    # Delete actual file if it exists
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        # Log error but don't fail the deletion
        print(f"Error deleting image file {file_path}: {e}")
    
    return True


def set_primary_image(db: Session, image_id: uuid.UUID) -> bool:
    """Set an image as primary for its shop product"""
    db_image = get_shop_product_image(db, image_id)
    if not db_image:
        return False
    
    # Remove primary status from all other images for this product
    db.query(ShopProductImage).filter(
        ShopProductImage.shop_product_id == db_image.shop_product_id
    ).update({"is_primary": False})
    
    # Set this image as primary
    db_image.is_primary = True
    db.add(db_image)
    db.commit()
    
    return True


def reorder_images(db: Session, shop_product_id: uuid.UUID, image_orders: List[dict]) -> bool:
    """
    Reorder images for a shop product
    
    Args:
        db: Database session
        shop_product_id: ID of the shop product
        image_orders: List of dicts with 'image_id' and 'display_order'
    """
    try:
        for item in image_orders:
            image_id = item.get("image_id")
            display_order = item.get("display_order")
            
            if image_id and display_order is not None:
                db.query(ShopProductImage).filter(
                    and_(
                        ShopProductImage.id == image_id,
                        ShopProductImage.shop_product_id == shop_product_id
                    )
                ).update({"display_order": display_order})
        
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False