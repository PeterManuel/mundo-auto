from datetime import datetime
from typing import List, Optional, Dict
import uuid
import random
import string

from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem, OrderStatus, OrderStatusUpdate, PaymentStatus
from app.models.cart import CartItem


def generate_order_number():
    # Generate a unique order number: current timestamp + 5 random characters
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return f"ORD-{timestamp}-{random_chars}"


def create_order_from_cart(
    db: Session,
    user_id: uuid.UUID,
    shipping_address: str,
    billing_address: str,
    payment_method: str,
    notes: Optional[str] = None
) -> Order:
    # Get cart items
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    
    if not cart_items:
        raise ValueError("Cart is empty")
    
    # Calculate total amount
    total_amount = 0
    for item in cart_items:
        shop_product = item.shop_product
        if shop_product:
            # Use shop product price (sale_price has priority over regular price)
            price = shop_product.sale_price if shop_product.sale_price else shop_product.price
            total_amount += price * item.quantity
    
    # Create order
    new_order = Order(
        user_id=user_id,
        order_number=generate_order_number(),
        total_amount=total_amount,
        shipping_address=shipping_address,
        billing_address=billing_address,
        payment_method=payment_method,
        notes=notes
    )
    
    db.add(new_order)
    db.flush()  # Get ID without committing
    
    # Create order items from cart
    order_items = []
    for cart_item in cart_items:
        shop_product = cart_item.shop_product
        
        if shop_product:
            # Use shop product price (sale_price has priority over regular price)
            price = shop_product.sale_price if shop_product.sale_price else shop_product.price
            
            order_item = OrderItem(
                order_id=new_order.id,
                shop_product_id=shop_product.id,
                quantity=cart_item.quantity,
                price=price,
                product_name=shop_product.name,
                shop_name=shop_product.shop.name
            )
            
            # Update shop inventory
            shop_product.stock_quantity = max(0, shop_product.stock_quantity - cart_item.quantity)
            db.add(shop_product)
            
            order_items.append(order_item)
    
    # Add order items
    db.add_all(order_items)
    
    # Add initial status update
    status_update = OrderStatusUpdate(
        order_id=new_order.id,
        status=OrderStatus.PENDING,
        comment="Order created"
    )
    db.add(status_update)
    
    # Clear cart
    for item in cart_items:
        db.delete(item)
    
    # Commit transaction
    db.commit()
    db.refresh(new_order)
    
    return new_order


def get_order(db: Session, order_id: uuid.UUID, user_id: Optional[uuid.UUID] = None) -> Optional[Order]:
    query = db.query(Order).filter(Order.id == order_id)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    return query.first()


def get_order_by_number(db: Session, order_number: str, user_id: Optional[uuid.UUID] = None) -> Optional[Order]:
    query = db.query(Order).filter(Order.order_number == order_number)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    return query.first()


def get_user_orders(
    db: Session, 
    user_id: uuid.UUID, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[OrderStatus] = None
) -> List[Order]:
    query = db.query(Order).filter(Order.user_id == user_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def update_order_status(
    db: Session, 
    order_id: uuid.UUID, 
    status: OrderStatus, 
    comment: Optional[str] = None
) -> Order:
    order = get_order(db, order_id)
    
    if not order:
        raise ValueError("Order not found")
    
    # Update order status
    order.status = status
    
    # Add status update
    status_update = OrderStatusUpdate(
        order_id=order.id,
        status=status,
        comment=comment
    )
    db.add(status_update)
    
    # Update order
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order


def update_payment_status(
    db: Session, 
    order_id: uuid.UUID, 
    payment_status: PaymentStatus
) -> Order:
    order = get_order(db, order_id)
    
    if not order:
        raise ValueError("Order not found")
    
    # Update payment status
    order.payment_status = payment_status
    
    # Add status update
    comment = f"Payment status updated to {payment_status.value}"
    status_update = OrderStatusUpdate(
        order_id=order.id,
        status=order.status,
        comment=comment
    )
    db.add(status_update)
    
    # Update order
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order


def update_shipping_info(
    db: Session, 
    order_id: uuid.UUID, 
    tracking_number: str,
    shipping_company: str
) -> Order:
    order = get_order(db, order_id)
    
    if not order:
        raise ValueError("Order not found")
    
    # Update shipping info
    order.tracking_number = tracking_number
    order.shipping_company = shipping_company
    
    # Update status if order is not yet shipped
    if order.status == OrderStatus.PENDING or order.status == OrderStatus.PROCESSING:
        order.status = OrderStatus.SHIPPED
        
        # Add status update
        status_update = OrderStatusUpdate(
            order_id=order.id,
            status=OrderStatus.SHIPPED,
            comment=f"Order shipped via {shipping_company}, tracking: {tracking_number}"
        )
        db.add(status_update)
    
    # Update order
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order