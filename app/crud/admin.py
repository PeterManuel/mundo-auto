from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

from sqlalchemy import func, desc, and_
from sqlalchemy.orm import Session

from app.models.admin import Banner, SystemSetting, Report
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.product import Product
from app.models.shop import Shop
from app.models.user import User
from app.models.shop_product import ShopProduct
from app.schemas.admin import BannerCreate, BannerUpdate, SystemSettingUpdate, ReportCreate


# Banner CRUD
def create_banner(db: Session, banner: BannerCreate) -> Banner:
    db_banner = Banner(**banner.dict())
    db.add(db_banner)
    db.commit()
    db.refresh(db_banner)
    return db_banner


def get_banner(db: Session, banner_id: uuid.UUID) -> Optional[Banner]:
    return db.query(Banner).filter(Banner.id == banner_id).first()


def get_active_banners(db: Session, position: Optional[str] = None) -> List[Banner]:
    query = db.query(Banner).filter(Banner.is_active == True)
    
    if position:
        query = query.filter(Banner.position == position)
    
    # Filter by date range if applicable
    current_time = datetime.utcnow()
    query = query.filter(
        (Banner.start_date.is_(None) | (Banner.start_date <= current_time)) &
        (Banner.end_date.is_(None) | (Banner.end_date >= current_time))
    )
    
    return query.all()


def update_banner(db: Session, banner_id: uuid.UUID, banner: BannerUpdate) -> Optional[Banner]:
    db_banner = get_banner(db, banner_id)
    if not db_banner:
        return None
    
    update_data = banner.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_banner, field, value)
    
    db.add(db_banner)
    db.commit()
    db.refresh(db_banner)
    return db_banner


def delete_banner(db: Session, banner_id: uuid.UUID) -> bool:
    db_banner = get_banner(db, banner_id)
    if not db_banner:
        return False
    
    db.delete(db_banner)
    db.commit()
    return True


# System Settings CRUD
def get_system_setting(db: Session, key: str) -> Optional[SystemSetting]:
    return db.query(SystemSetting).filter(SystemSetting.key == key).first()


def get_all_system_settings(db: Session) -> List[SystemSetting]:
    return db.query(SystemSetting).all()


def update_system_setting(db: Session, key: str, setting: SystemSettingUpdate) -> SystemSetting:
    db_setting = get_system_setting(db, key)
    
    if not db_setting:
        # Create if doesn't exist
        db_setting = SystemSetting(
            key=key,
            value=setting.value,
            description=setting.description
        )
    else:
        # Update existing
        db_setting.value = setting.value
        if setting.description:
            db_setting.description = setting.description
    
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting


# Dashboard Statistics
def get_dashboard_stats(db: Session, shop_id: Optional[uuid.UUID] = None) -> Dict[str, Any]:
    # Date ranges
    now = datetime.utcnow()
    last_month = now - timedelta(days=30)
    
    # Base queries that may be filtered by shop
    orders_query = db.query(Order)
    shop_products_query = db.query(ShopProduct)
    
    # If shop_id is provided, filter all queries by that shop
    if shop_id:
        # Join with OrderItem to filter by shop_id
        orders_query = orders_query.join(OrderItem).filter(OrderItem.shop_id == shop_id)
        shop_products_query = shop_products_query.filter(ShopProduct.shop_id == shop_id)
    
    # Total sales
    total_sales = orders_query.with_entities(func.sum(Order.total_amount)).scalar() or 0
    
    # Total orders
    total_orders = orders_query.count() or 0
    
    # Pending orders
    pending_orders = (
        orders_query
        .filter(Order.status.in_([OrderStatus.PENDING, OrderStatus.PROCESSING]))
        .count()
    ) or 0
    
    # Total products (distinct products in this shop or all shops)
    if shop_id:
        total_products = (
            shop_products_query.with_entities(func.count(func.distinct(ShopProduct.product_id)))
            .scalar()
        ) or 0
    else:
        total_products = db.query(func.count(Product.id)).scalar() or 0
    
    # Low stock products - now using ShopProduct for stock info
    low_stock_threshold = 5  # Define threshold for low stock
    low_stock_products = (
        shop_products_query
        .filter(ShopProduct.stock_quantity <= low_stock_threshold)
        .count()
    ) or 0
    
    # Active users (for shop-specific, only count users associated with the shop)
    if shop_id:
        active_users = (
            db.query(func.count(User.id))
            .filter(User.is_active == True, User.shop_id == shop_id)
            .scalar()
        ) or 0
    else:
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    
    # Top selling products (last 30 days)
    top_products = []
    
    # Base query for top products
    top_products_base_query = (
        db.query(
            Product.id,
            Product.name,
            Product.price,
            func.sum(OrderItem.quantity).label("total_quantity"),
            func.sum(OrderItem.price * OrderItem.quantity).label("total_sales")
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, and_(
            Order.id == OrderItem.order_id,
            Order.created_at >= last_month
        ))
    )
    
    # Apply shop filter if needed
    if shop_id:
        top_products_base_query = top_products_base_query.filter(OrderItem.shop_id == shop_id)
    
    # Complete the query with grouping and ordering
    top_products_query = (
        top_products_base_query
        .group_by(Product.id, Product.name, Product.price)
        .order_by(desc("total_quantity"))
        .limit(5)
        .all()
    )
    
    for product in top_products_query:
        top_products.append({
            "id": str(product.id),
            "name": product.name,
            "price": product.price,
            "total_quantity": product.total_quantity,
            "total_sales": product.total_sales
        })
    
    # Recent orders
    recent_orders = []
    
    # Base query for recent orders
    recent_orders_base_query = (
        db.query(
            Order.id,
            Order.order_number,
            Order.total_amount,
            Order.status,
            Order.created_at,
            User.email.label("user_email")
        )
        .join(User, User.id == Order.user_id)
    )
    
    # Apply shop filter if needed
    if shop_id:
        recent_orders_base_query = recent_orders_base_query.join(OrderItem).filter(OrderItem.shop_id == shop_id)
    
    # Complete the query with ordering and limit
    recent_orders_query = (
        recent_orders_base_query
        .order_by(desc(Order.created_at))
        .limit(5)
        .all()
    )
    
    for order in recent_orders_query:
        recent_orders.append({
            "id": str(order.id),
            "order_number": order.order_number,
            "total_amount": order.total_amount,
            "status": order.status.value,
            "created_at": order.created_at.isoformat(),
            "user_email": order.user_email
        })
    
    # Get shop info if shop_id is provided
    shop_name = None
    if shop_id:
        shop = db.query(Shop).filter(Shop.id == shop_id).first()
        if shop:
            shop_name = shop.name
    
    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_products": total_products,
        "low_stock_products": low_stock_products,
        "active_users": active_users,
        "top_selling_products": top_products,
        "recent_orders": recent_orders,
        "shop_id": shop_id,
        "shop_name": shop_name
    }


# Report CRUD
def create_report(db: Session, report: ReportCreate, created_by: uuid.UUID) -> Report:
    db_report = Report(
        **report.dict(),
        created_by=created_by
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_report(db: Session, report_id: uuid.UUID) -> Optional[Report]:
    return db.query(Report).filter(Report.id == report_id).first()


def get_reports(db: Session, skip: int = 0, limit: int = 100) -> List[Report]:
    return db.query(Report).offset(skip).limit(limit).all()


def delete_report(db: Session, report_id: uuid.UUID) -> bool:
    db_report = get_report(db, report_id)
    if not db_report:
        return False
    
    db.delete(db_report)
    db.commit()
    return True