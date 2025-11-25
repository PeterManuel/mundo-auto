from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud.analytics import (
    get_best_selling_products_by_shop,
    get_most_active_customers_by_shop,
    get_low_stock_products_by_shop
)
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.analytics import (
    BestSellingProduct,
    MostActiveCustomer,
    LowStockProduct
)

router = APIRouter()


def check_shop_access(current_user: User, shop_id: uuid.UUID) -> bool:
    """
    Check if user has access to the shop analytics
    """
    # Superadmin has access to all shops
    if current_user.role == UserRole.SUPERADMIN:
        return True
    
    # Admin has access to all shops  
    if current_user.role == UserRole.ADMIN:
        return True
    
    # Logist has access only to their assigned shop
    if current_user.role == UserRole.LOGIST:
        return str(current_user.shop_id) == str(shop_id)
    
    # Other users don't have access
    return False


@router.get("/best-selling-products", response_model=List[BestSellingProduct])
def get_best_selling_products(
    shop_id: uuid.UUID = Query(..., description="Shop ID to get analytics for"),
    days: int = Query(30, description="Number of days to look back", ge=1, le=365),
    limit: int = Query(10, description="Maximum number of products to return", ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get best-selling products for a specific shop.
    
    For logists: Can only access their assigned shop's data.
    For admins/superadmins: Can access any shop's data.
    """
    # Check access permissions
    if not check_shop_access(current_user, shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this shop's analytics"
        )
    
    # If user is a logist, ensure they can only access their assigned shop
    if current_user.role == UserRole.LOGIST:
        if not current_user.shop_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to any shop"
            )
        shop_id = current_user.shop_id
    
    products = get_best_selling_products_by_shop(db, shop_id, days, limit)
    return products


@router.get("/most-active-customers", response_model=List[MostActiveCustomer])
def get_most_active_customers(
    shop_id: uuid.UUID = Query(..., description="Shop ID to get analytics for"),
    days: int = Query(30, description="Number of days to look back", ge=1, le=365),
    limit: int = Query(10, description="Maximum number of customers to return", ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get most active customers for a specific shop.
    
    For logists: Can only access their assigned shop's data.
    For admins/superadmins: Can access any shop's data.
    """
    # Check access permissions
    if not check_shop_access(current_user, shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this shop's analytics"
        )
    
    # If user is a logist, ensure they can only access their assigned shop
    if current_user.role == UserRole.LOGIST:
        if not current_user.shop_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to any shop"
            )
        shop_id = current_user.shop_id
    
    customers = get_most_active_customers_by_shop(db, shop_id, days, limit)
    return customers


@router.get("/low-stock-products", response_model=List[LowStockProduct])
def get_low_stock_products(
    shop_id: uuid.UUID = Query(..., description="Shop ID to get analytics for"),
    threshold: int = Query(5, description="Stock threshold (products with stock <= threshold)", ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get products with low stock for a specific shop.
    
    For logists: Can only access their assigned shop's data.
    For admins/superadmins: Can access any shop's data.
    """
    # Check access permissions
    if not check_shop_access(current_user, shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this shop's analytics"
        )
    
    # If user is a logist, ensure they can only access their assigned shop
    if current_user.role == UserRole.LOGIST:
        if not current_user.shop_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to any shop"
            )
        shop_id = current_user.shop_id
    
    products = get_low_stock_products_by_shop(db, shop_id, threshold)
    return products


# Convenience endpoints for logists (automatically use their assigned shop)
@router.get("/my-shop/best-selling-products", response_model=List[BestSellingProduct])
def get_my_shop_best_selling_products(
    days: int = Query(30, description="Number of days to look back", ge=1, le=365),
    limit: int = Query(10, description="Maximum number of products to return", ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get best-selling products for the current logist's assigned shop.
    Only accessible by logist users.
    """
    if current_user.role != UserRole.LOGIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available for logist users"
        )
    
    if not current_user.shop_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to any shop"
        )
    
    products = get_best_selling_products_by_shop(db, current_user.shop_id, days, limit)
    return products


@router.get("/my-shop/most-active-customers", response_model=List[MostActiveCustomer])
def get_my_shop_most_active_customers(
    days: int = Query(30, description="Number of days to look back", ge=1, le=365),
    limit: int = Query(10, description="Maximum number of customers to return", ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get most active customers for the current logist's assigned shop.
    Only accessible by logist users.
    """
    if current_user.role != UserRole.LOGIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available for logist users"
        )
    
    if not current_user.shop_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to any shop"
        )
    
    customers = get_most_active_customers_by_shop(db, current_user.shop_id, days, limit)
    return customers


@router.get("/my-shop/low-stock-products", response_model=List[LowStockProduct])
def get_my_shop_low_stock_products(
    threshold: int = Query(5, description="Stock threshold (products with stock <= threshold)", ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get products with low stock for the current logist's assigned shop.
    Only accessible by logist users.
    """
    if current_user.role != UserRole.LOGIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is only available for logist users"
        )
    
    if not current_user.shop_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to any shop"
        )
    
    products = get_low_stock_products_by_shop(db, current_user.shop_id, threshold)
    return products