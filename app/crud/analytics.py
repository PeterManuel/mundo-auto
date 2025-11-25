from datetime import datetime, timedelta
from typing import List, Optional
import uuid

from sqlalchemy import func, desc, and_
from sqlalchemy.orm import Session

from app.models.order import Order, OrderItem
from app.models.shop_product import ShopProduct
from app.models.user import User
from app.models.shop import Shop


def get_best_selling_products_by_shop(
    db: Session, 
    shop_id: uuid.UUID, 
    days: int = 30, 
    limit: int = 10
) -> List[dict]:
    """
    Get best-selling products for a specific shop based on quantity sold
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Query to get best-selling products by quantity
    query = (
        db.query(
            ShopProduct.id,
            ShopProduct.name,
            ShopProduct.brand,
            ShopProduct.model,
            ShopProduct.oe_number,
            ShopProduct.price,
            Shop.name.label("shop_name"),
            func.sum(OrderItem.quantity).label("total_quantity_sold"),
            func.sum(OrderItem.price * OrderItem.quantity).label("total_revenue")
        )
        .join(OrderItem, OrderItem.shop_product_id == ShopProduct.id)
        .join(Order, and_(
            Order.id == OrderItem.order_id,
            Order.created_at >= start_date
        ))
        .join(Shop, Shop.id == ShopProduct.shop_id)
        .filter(ShopProduct.shop_id == shop_id)
        .filter(ShopProduct.is_active == True)
        .group_by(
            ShopProduct.id, 
            ShopProduct.name, 
            ShopProduct.brand,
            ShopProduct.model,
            ShopProduct.oe_number,
            ShopProduct.price,
            Shop.name
        )
        .order_by(desc("total_quantity_sold"))
        .limit(limit)
    )
    
    results = query.all()
    
    return [
        {
            "id": result.id,
            "name": result.name,
            "brand": result.brand,
            "model": result.model,
            "oe_number": result.oe_number,
            "price": result.price,
            "total_quantity_sold": result.total_quantity_sold,
            "total_revenue": float(result.total_revenue or 0),
            "shop_name": result.shop_name
        }
        for result in results
    ]


def get_most_active_customers_by_shop(
    db: Session, 
    shop_id: uuid.UUID, 
    days: int = 30, 
    limit: int = 10
) -> List[dict]:
    """
    Get most active customers for a specific shop based on order count and total spent
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Subquery to get orders that contain products from the specific shop
    shop_orders_subquery = (
        db.query(Order.id)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .join(ShopProduct, ShopProduct.id == OrderItem.shop_product_id)
        .filter(ShopProduct.shop_id == shop_id)
        .filter(Order.created_at >= start_date)
        .subquery()
    )
    
    # Query to get most active customers
    query = (
        db.query(
            User.id,
            User.email,
            User.first_name,
            User.last_name,
            func.count(Order.id).label("total_orders"),
            func.sum(Order.total_amount).label("total_spent"),
            func.max(Order.created_at).label("last_order_date")
        )
        .join(Order, Order.user_id == User.id)
        .filter(Order.id.in_(shop_orders_subquery))
        .group_by(User.id, User.email, User.first_name, User.last_name)
        .order_by(desc("total_orders"), desc("total_spent"))
        .limit(limit)
    )
    
    results = query.all()
    
    return [
        {
            "id": result.id,
            "email": result.email,
            "first_name": result.first_name,
            "last_name": result.last_name,
            "total_orders": result.total_orders,
            "total_spent": float(result.total_spent or 0),
            "last_order_date": result.last_order_date
        }
        for result in results
    ]


def get_low_stock_products_by_shop(
    db: Session, 
    shop_id: uuid.UUID, 
    threshold: int = 5
) -> List[dict]:
    """
    Get products with low stock for a specific shop
    """
    query = (
        db.query(
            ShopProduct.id,
            ShopProduct.name,
            ShopProduct.brand,
            ShopProduct.model,
            ShopProduct.oe_number,
            ShopProduct.price,
            ShopProduct.stock_quantity.label("current_stock"),
            ShopProduct.is_active,
            Shop.name.label("shop_name")
        )
        .join(Shop, Shop.id == ShopProduct.shop_id)
        .filter(ShopProduct.shop_id == shop_id)
        .filter(ShopProduct.stock_quantity <= threshold)
        .order_by(ShopProduct.stock_quantity.asc(), ShopProduct.name)
    )
    
    results = query.all()
    
    return [
        {
            "id": result.id,
            "name": result.name,
            "brand": result.brand,
            "model": result.model,
            "oe_number": result.oe_number,
            "price": result.price,
            "current_stock": result.current_stock,
            "shop_name": result.shop_name,
            "is_active": result.is_active
        }
        for result in results
    ]