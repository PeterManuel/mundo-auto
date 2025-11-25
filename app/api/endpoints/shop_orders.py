from typing import List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud.order import (
    get_shop_orders,
    get_shop_order_history_by_customer,
    count_shop_orders,
    update_order_status,
    update_payment_status,
    update_shipping_info,
    get_order,
    get_orders_by_shop_and_status,
    get_shop_customers_with_orders,
    get_shop_order_analytics
)
from app.crud.user import get_user
from app.crud.shop import get_shop
from app.db.session import get_db
from app.models.order import OrderStatus, PaymentStatus
from app.models.user import User, UserRole
from app.schemas.order import (
    OrderResponse,
    OrderUpdate,
    OrderFilter,
    OrderStatusUpdate,
    ShopOrderSummary,
    CustomerOrderHistory
)

router = APIRouter()


def check_shop_access(current_user: User, shop_id: uuid.UUID) -> bool:
    """
    Check if user has access to the shop
    """
    # Superadmin has access to all shops
    if current_user.role == UserRole.SUPERADMIN:
        return True
    
    # Logist has access only to their assigned shop
    if current_user.role == UserRole.LOGIST:
        return str(current_user.shop_id) == str(shop_id)
    
    # Admin has access to all shops
    if current_user.role == UserRole.ADMIN:
        return True
    
    # Other users don't have access
    return False


@router.get("/{shop_id}/orders", response_model=List[OrderResponse])
def get_shop_orders_endpoint(
    shop_id: uuid.UUID,
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    customer_id: Optional[uuid.UUID] = Query(None, description="Filter by customer ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all orders for a specific shop
    """
    # Check access
    if not check_shop_access(current_user, shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this shop's orders"
        )
    
    # Verify shop exists
    shop = get_shop(db, shop_id)
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    orders = get_shop_orders(db, shop_id, skip, limit, status, customer_id)
    return orders


@router.get("/{shop_id}/orders/summary", response_model=ShopOrderSummary)
def get_shop_orders_summary(
    shop_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get order summary for a shop
    """
    # Check access
    if not check_shop_access(current_user, shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this shop's orders"
        )
    
    # Verify shop exists
    shop = get_shop(db, shop_id)
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    # Get order counts by status
    total_orders = count_shop_orders(db, shop_id)
    pending_orders = count_shop_orders(db, shop_id, OrderStatus.PENDING)
    processing_orders = count_shop_orders(db, shop_id, OrderStatus.PROCESSING)
    shipped_orders = count_shop_orders(db, shop_id, OrderStatus.SHIPPED)
    delivered_orders = count_shop_orders(db, shop_id, OrderStatus.DELIVERED)
    cancelled_orders = count_shop_orders(db, shop_id, OrderStatus.CANCELLED)
    
    # Calculate total revenue (from delivered orders only)
    delivered_order_list = get_orders_by_shop_and_status(db, shop_id, [OrderStatus.DELIVERED])
    total_revenue = sum([order.total_amount for order in delivered_order_list])
    
    return ShopOrderSummary(
        total_orders=total_orders,
        pending_orders=pending_orders,
        processing_orders=processing_orders,
        shipped_orders=shipped_orders,
        delivered_orders=delivered_orders,
        cancelled_orders=cancelled_orders,
        total_revenue=total_revenue
    )


@router.get("/{shop_id}/orders/{order_id}", response_model=OrderResponse)
def get_shop_order(
    shop_id: uuid.UUID,
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific order from a shop
    """
    # Check access
    if not check_shop_access(current_user, shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this shop's orders"
        )
    
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify the order contains items from this shop
    has_shop_items = any(
        str(item.shop_product.shop_id) == str(shop_id) 
        for item in order.items 
        if item.shop_product
    )
    
    if not has_shop_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found in this shop"
        )
    
    return order


@router.put("/{shop_id}/orders/{order_id}/status", response_model=OrderResponse)
def update_shop_order_status(
    shop_id: uuid.UUID,
    order_id: uuid.UUID,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update order status for a shop order
    """
    # Check access
    if not check_shop_access(current_user, shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this shop's orders"
        )
    
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify the order contains items from this shop
    has_shop_items = any(
        str(item.shop_product.shop_id) == str(shop_id) 
        for item in order.items 
        if item.shop_product
    )
    
    if not has_shop_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found in this shop"
        )
    
    # Check if status transition is valid
    current_status = order.status
    new_status = status_update.status
    
    # Define valid status transitions
    valid_transitions = {
        OrderStatus.PENDING: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
        OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
        OrderStatus.SHIPPED: [OrderStatus.DELIVERED, OrderStatus.RETURNED],
        OrderStatus.DELIVERED: [OrderStatus.RETURNED],
        OrderStatus.CANCELLED: [],  # Can't change from cancelled
        OrderStatus.RETURNED: []    # Can't change from returned
    }
    
    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {current_status} to {new_status}"
        )
    
    updated_order = update_order_status(db, order_id, new_status, status_update.comment)
    return updated_order


@router.put("/{shop_id}/orders/{order_id}/payment", response_model=OrderResponse)
def update_shop_order_payment_status(
    shop_id: uuid.UUID,
    order_id: uuid.UUID,
    payment_status: PaymentStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update payment status for a shop order
    """
    # Check access
    if not check_shop_access(current_user, shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this shop's orders"
        )
    
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify the order contains items from this shop
    has_shop_items = any(
        str(item.shop_product.shop_id) == str(shop_id) 
        for item in order.items 
        if item.shop_product
    )
    
    if not has_shop_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found in this shop"
        )
    
    updated_order = update_payment_status(db, order_id, payment_status)
    return updated_order


@router.get("/{shop_id}/customers/{customer_id}/orders", response_model=CustomerOrderHistory)
def get_customer_order_history(
    shop_id: uuid.UUID,
    customer_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get order history for a specific customer in a shop
    """
    # Check access
    if not check_shop_access(current_user, shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this shop's customer data"
        )
    
    # Verify shop exists
    shop = get_shop(db, shop_id)
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    # Verify customer exists
    customer = get_user(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Get customer orders for this shop
    orders = get_shop_order_history_by_customer(db, shop_id, customer_id, skip, limit)
    
    # Calculate statistics
    total_orders = count_shop_orders(db, shop_id, user_id=customer_id)
    total_spent = sum([order.total_amount for order in orders if order.status == OrderStatus.DELIVERED])
    last_order_date = orders[0].created_at if orders else None
    
    return CustomerOrderHistory(
        customer_id=customer_id,
        customer_name=f"{customer.first_name or ''} {customer.last_name or ''}".strip() or customer.email,
        customer_email=customer.email,
        total_orders=total_orders,
        total_spent=total_spent,
        last_order_date=last_order_date,
        orders=orders
    )


@router.put("/{shop_id}/orders/{order_id}/shipping", response_model=OrderResponse)
def update_shop_order_shipping(
    shop_id: uuid.UUID,
    order_id: uuid.UUID,
    tracking_number: str,
    shipping_company: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update shipping information for a shop order
    """
    # Check access
    if not check_shop_access(current_user, shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this shop's orders"
        )
    
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify the order contains items from this shop
    has_shop_items = any(
        str(item.shop_product.shop_id) == str(shop_id) 
        for item in order.items 
        if item.shop_product
    )
    
    if not has_shop_items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found in this shop"
        )
    
    updated_order = update_shipping_info(db, order_id, tracking_number, shipping_company)
    return updated_order


@router.get("/{shop_id}/customers", response_model=List[dict])
def get_shop_customers(
    shop_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all customers who have made orders from this shop
    """
    # Check access
    if not check_shop_access(current_user, shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this shop's customer data"
        )
    
    # Verify shop exists
    shop = get_shop(db, shop_id)
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    customers = get_shop_customers_with_orders(db, shop_id, skip, limit)
    return customers


@router.get("/{shop_id}/analytics", response_model=dict)
def get_shop_analytics(
    shop_id: uuid.UUID,
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get analytics data for shop orders
    """
    # Check access
    if not check_shop_access(current_user, shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this shop's analytics"
        )
    
    # Verify shop exists
    shop = get_shop(db, shop_id)
    if not shop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shop not found"
        )
    
    analytics = get_shop_order_analytics(db, shop_id, start_date, end_date)
    return analytics