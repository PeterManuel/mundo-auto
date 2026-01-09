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
) -> List[Order]:
    """
    Create orders from cart, grouping items by shop.
    Each shop will have its own separate order.
    Returns a list of created orders.
    """
    # Get cart items
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    
    if not cart_items:
        raise ValueError("Cart is empty")
    
    # Group cart items by shop
    items_by_shop: Dict[uuid.UUID, List[CartItem]] = {}
    for item in cart_items:
        shop_product = item.shop_product
        if shop_product:
            shop_id = shop_product.shop_id
            if shop_id not in items_by_shop:
                items_by_shop[shop_id] = []
            items_by_shop[shop_id].append(item)
    
    created_orders: List[Order] = []
    
    # Create separate order for each shop
    for shop_id, shop_cart_items in items_by_shop.items():
        # Calculate total amount for this shop's order
        total_amount = 0
        for item in shop_cart_items:
            shop_product = item.shop_product
            if shop_product:
                price = shop_product.sale_price if shop_product.sale_price else shop_product.price
                total_amount += price * item.quantity
        
        # Get shop name for notes
        shop_name = shop_cart_items[0].shop_product.shop.name if shop_cart_items else "Unknown Shop"
        
        # Create order for this shop
        order_notes = f"Order from {shop_name}"
        if notes:
            order_notes = f"{order_notes}. Customer notes: {notes}"
        
        new_order = Order(
            user_id=user_id,
            order_number=generate_order_number(),
            total_amount=total_amount,
            shipping_address=shipping_address,
            billing_address=billing_address,
            payment_method=payment_method,
            notes=order_notes
        )
        
        db.add(new_order)
        db.flush()  # Get ID without committing
        
        # Create order items for this shop
        order_items = []
        for cart_item in shop_cart_items:
            shop_product = cart_item.shop_product
            
            if shop_product:
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
            comment=f"Order created for shop: {shop_name}"
        )
        db.add(status_update)
        
        created_orders.append(new_order)
    
    # Clear cart (all items)
    for item in cart_items:
        db.delete(item)
    
    # Commit transaction
    db.commit()
    
    # Refresh all orders
    for order in created_orders:
        db.refresh(order)
    
    return created_orders


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


def get_shop_orders(
    db: Session,
    shop_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    status: Optional[OrderStatus] = None,
    user_id: Optional[uuid.UUID] = None
) -> List[Order]:
    """
    Get all orders that contain products from a specific shop
    """
    from app.models.shop_product import ShopProduct
    
    query = (
        db.query(Order)
        .join(OrderItem)
        .join(ShopProduct, OrderItem.shop_product_id == ShopProduct.id)
        .filter(ShopProduct.shop_id == shop_id)
    )
    
    if status:
        query = query.filter(Order.status == status)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    return query.distinct().order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def get_shop_order_history_by_customer(
    db: Session,
    shop_id: uuid.UUID,
    customer_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> List[Order]:
    """
    Get order history for a specific customer for a specific shop
    """
    from app.models.shop_product import ShopProduct
    
    return (
        db.query(Order)
        .join(OrderItem)
        .join(ShopProduct, OrderItem.shop_product_id == ShopProduct.id)
        .filter(ShopProduct.shop_id == shop_id)
        .filter(Order.user_id == customer_id)
        .distinct()
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def count_shop_orders(
    db: Session,
    shop_id: uuid.UUID,
    status: Optional[OrderStatus] = None,
    user_id: Optional[uuid.UUID] = None
) -> int:
    """
    Count orders for a specific shop
    """
    from app.models.shop_product import ShopProduct
    
    query = (
        db.query(Order)
        .join(OrderItem)
        .join(ShopProduct, OrderItem.shop_product_id == ShopProduct.id)
        .filter(ShopProduct.shop_id == shop_id)
    )
    
    if status:
        query = query.filter(Order.status == status)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    return query.distinct().count()


def get_orders_by_shop_and_status(
    db: Session,
    shop_id: uuid.UUID,
    status_list: List[OrderStatus],
    skip: int = 0,
    limit: int = 100
) -> List[Order]:
    """
    Get orders by shop and multiple status
    """
    from app.models.shop_product import ShopProduct
    
    return (
        db.query(Order)
        .join(OrderItem)
        .join(ShopProduct, OrderItem.shop_product_id == ShopProduct.id)
        .filter(ShopProduct.shop_id == shop_id)
        .filter(Order.status.in_(status_list))
        .distinct()
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_shop_customers_with_orders(
    db: Session,
    shop_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100
) -> List[Dict]:
    """
    Get all customers who have made orders from a specific shop
    """
    from sqlalchemy import func
    from app.models.user import User
    from app.models.shop_product import ShopProduct
    
    result = (
        db.query(
            User.id,
            User.first_name,
            User.last_name,
            User.email,
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_spent'),
            func.max(Order.created_at).label('last_order_date')
        )
        .join(Order, User.id == Order.user_id)
        .join(OrderItem, Order.id == OrderItem.order_id)
        .join(ShopProduct, OrderItem.shop_product_id == ShopProduct.id)
        .filter(ShopProduct.shop_id == shop_id)
        .filter(Order.status != OrderStatus.CANCELLED)
        .group_by(User.id, User.first_name, User.last_name, User.email)
        .order_by(func.max(Order.created_at).desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return [
        {
            'customer_id': row.id,
            'customer_name': f"{row.first_name or ''} {row.last_name or ''}".strip() or row.email,
            'customer_email': row.email,
            'total_orders': row.total_orders,
            'total_spent': float(row.total_spent or 0),
            'last_order_date': row.last_order_date
        }
        for row in result
    ]


def get_shop_order_analytics(
    db: Session,
    shop_id: uuid.UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """
    Get analytics data for shop orders
    """
    from app.models.shop_product import ShopProduct
    
    query = (
        db.query(Order)
        .join(OrderItem)
        .join(ShopProduct, OrderItem.shop_product_id == ShopProduct.id)
        .filter(ShopProduct.shop_id == shop_id)
    )
    
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    
    # Get orders by status
    orders_by_status = {}
    for status in OrderStatus:
        count = query.filter(Order.status == status).count()
        orders_by_status[status.value] = count
    
    # Get revenue data (only from delivered orders)
    delivered_orders = query.filter(Order.status == OrderStatus.DELIVERED).all()
    total_revenue = sum([order.total_amount for order in delivered_orders])
    
    # Get average order value
    avg_order_value = total_revenue / len(delivered_orders) if delivered_orders else 0
    
    # Get orders per day (last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_orders = query.filter(Order.created_at >= thirty_days_ago).all()
    
    # Group by date
    orders_per_day = {}
    for order in recent_orders:
        date_key = order.created_at.strftime('%Y-%m-%d')
        orders_per_day[date_key] = orders_per_day.get(date_key, 0) + 1
    
    return {
        'orders_by_status': orders_by_status,
        'total_revenue': total_revenue,
        'average_order_value': avg_order_value,
        'total_delivered_orders': len(delivered_orders),
        'orders_per_day': orders_per_day
    }