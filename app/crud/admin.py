from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uuid

from sqlalchemy import func, desc, and_
from sqlalchemy.orm import Session

from app.models.admin import Banner, SystemSetting, Report
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.product import Product
from app.models.user import User
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
def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    # Date ranges
    now = datetime.utcnow()
    last_month = now - timedelta(days=30)
    
    # Total sales
    total_sales = db.query(func.sum(Order.total_amount)).scalar() or 0
    
    # Total orders
    total_orders = db.query(func.count(Order.id)).scalar() or 0
    
    # Pending orders
    pending_orders = (
        db.query(func.count(Order.id))
        .filter(Order.status.in_([OrderStatus.PENDING, OrderStatus.PROCESSING]))
        .scalar()
    ) or 0
    
    # Total products
    total_products = db.query(func.count(Product.id)).scalar() or 0
    
    # Low stock products
    low_stock_threshold = 5  # Define threshold for low stock
    low_stock_products = (
        db.query(func.count(Product.id))
        .filter(Product.stock_quantity <= low_stock_threshold)
        .scalar()
    ) or 0
    
    # Active users
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
    
    # Top selling products (last 30 days)
    top_products = []
    top_products_query = (
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
    recent_orders_query = (
        db.query(
            Order.id,
            Order.order_number,
            Order.total_amount,
            Order.status,
            Order.created_at,
            User.email.label("user_email")
        )
        .join(User, User.id == Order.user_id)
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
    
    return {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "total_products": total_products,
        "low_stock_products": low_stock_products,
        "active_users": active_users,
        "top_selling_products": top_products,
        "recent_orders": recent_orders
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