from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud.shop import (
    get_shop,
    get_shop_by_slug,
    get_shops,
    create_shop,
    update_shop,
    delete_shop,
)
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.shop import ShopCreate, ShopUpdate, ShopResponse

router = APIRouter()


# Helper function to check if user is a superadmin
def is_superadmin(current_user: User) -> bool:
    """Check if user is a superadmin"""
    if current_user.role != UserRole.SUPERADMIN:
        return False
    return True


@router.get("/", response_model=List[ShopResponse])
def read_shops(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """
    Get all shops (public endpoint)
    """
    shops = get_shops(db, skip=skip, limit=limit, is_active=is_active)
    return shops


@router.get("/{shop_id_or_slug}", response_model=ShopResponse)
def read_shop(
    shop_id_or_slug: str,
    db: Session = Depends(get_db),
):
    """
    Get a specific shop by ID or slug (public endpoint)
    """
    # Check if the parameter is a UUID or a slug
    try:
        shop_id = uuid.UUID(shop_id_or_slug)
        shop = get_shop(db, shop_id)
    except ValueError:
        shop = get_shop_by_slug(db, shop_id_or_slug)
    
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    return shop


@router.post("/", response_model=ShopResponse, status_code=status.HTTP_201_CREATED)
def create_shop_endpoint(
    shop: ShopCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new shop (superadmin only)
    """
    if not is_superadmin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create shops"
        )
    
    db_shop = create_shop(db, shop)
    return db_shop


@router.put("/{shop_id}", response_model=ShopResponse)
def update_shop_endpoint(
    shop_id: uuid.UUID,
    shop: ShopUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a shop (superadmin only)
    """
    if not is_superadmin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update shops"
        )
    
    db_shop = update_shop(db, shop_id, shop)
    if not db_shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    return db_shop


@router.delete("/{shop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shop_endpoint(
    shop_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a shop (superadmin only)
    """
    if not is_superadmin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete shops"
        )
    
    success = delete_shop(db, shop_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    return