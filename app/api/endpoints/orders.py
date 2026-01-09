from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud.order import (
    create_order_from_cart,
    get_order,
    get_order_by_number,
    get_user_orders,
    update_order_status,
    update_payment_status,
    update_shipping_info
)
from app.db.session import get_db
from app.models.order import OrderStatus, PaymentStatus
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrdersCreatedResponse,
    OrderUpdate
)

router = APIRouter()


@router.post("/", response_model=OrdersCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create orders from the user's cart.
    Items are grouped by shop, creating separate orders for each shop.
    """
    try:
        db_orders = create_order_from_cart(
            db,
            current_user.id,
            order.shipping_address,
            order.billing_address,
            order.payment_method,
            order.notes
        )
        
        total_orders = len(db_orders)
        if total_orders == 1:
            message = "Order created successfully"
        else:
            message = f"{total_orders} orders created successfully (one per shop)"
        
        return OrdersCreatedResponse(
            orders=db_orders,
            total_orders=total_orders,
            message=message
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[OrderResponse])
def read_user_orders_endpoint(
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all orders for the current user
    """
    orders = get_user_orders(db, current_user.id, skip, limit, status)
    return orders


@router.get("/{order_id_or_number}", response_model=OrderResponse)
def read_order_endpoint(
    order_id_or_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific order by ID or order number
    """
    # Check if it's a UUID or an order number
    try:
        order_id = uuid.UUID(order_id_or_number)
        order = get_order(db, order_id, current_user.id)
    except ValueError:
        # Not a valid UUID, try as order number
        order = get_order_by_number(db, order_id_or_number, current_user.id)
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Check if user is authorized to view this order
    if str(order.user_id) != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this order")
    
    return order


@router.put("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel an order (if it's still in PENDING or PROCESSING status)
    """
    order = get_order(db, order_id, current_user.id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Check if user is authorized to cancel this order
    if str(order.user_id) != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this order")
    
    # Check if order can be cancelled
    if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status {order.status}"
        )
    
    # Update order status
    updated_order = update_order_status(db, order_id, OrderStatus.CANCELLED, "Cancelled by user")
    return updated_order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: uuid.UUID,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update order status, payment status or shipping info (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Update order fields
    update_data = order_update.dict(exclude_unset=True)
    
    # Update status if provided
    if "status" in update_data:
        order = update_order_status(
            db, 
            order_id, 
            update_data["status"], 
            update_data.get("notes")
        )
    
    # Update payment status if provided
    if "payment_status" in update_data:
        order = update_payment_status(db, order_id, update_data["payment_status"])
    
    # Update shipping info if provided
    if "tracking_number" in update_data and "shipping_company" in update_data:
        order = update_shipping_info(
            db,
            order_id,
            update_data["tracking_number"],
            update_data["shipping_company"]
        )
    
    return order