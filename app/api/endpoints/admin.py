from typing import List, Optional, Dict, Any
import uuid
from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile, Query, status
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud.admin import (
    get_dashboard_stats,
    create_banner,
    get_banner,
    get_active_banners,
    update_banner,
    delete_banner,
    get_system_setting,
    get_all_system_settings,
    update_system_setting,
    create_report,
    get_report,
    get_reports,
    delete_report
)
from app.crud.product import (
    get_products,
    create_product,
    update_product,
    delete_product
)
from app.crud.order import get_order, update_order_status, update_payment_status, update_shipping_info
from app.db.session import get_db
from app.models.order import OrderStatus, PaymentStatus
from app.models.user import User, UserRole
from app.schemas.admin import (
    BannerCreate,
    BannerUpdate,
    BannerResponse,
    SystemSettingBase,
    SystemSettingUpdate,
    SystemSettingResponse,
    ReportCreate,
    ReportResponse,
    DashboardSummary
)
from app.utils.file_upload import save_upload_file
from app.models.admin import Banner

router = APIRouter()


# Admin authentication check
def check_admin_access(current_user: User):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required"
        )


# Dashboard
@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard(
    shop_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics
    - For superadmins/admins: Can view global dashboard or specific shop stats by providing shop_id
    - For logist users: Can only view stats for their assigned shop
    """
    # Handle access control based on user role
    if current_user.role == UserRole.LOGIST:
        # Logist users can only see their assigned shop's dashboard
        if not current_user.shop_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to any shop"
            )
        
        # Force the shop_id parameter to be the logist's assigned shop
        shop_id = current_user.shop_id
        
    elif current_user.role in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        # Admin/Superadmin can see global dashboard or filter by shop_id
        pass
    else:
        # Other roles don't have access
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access dashboard"
        )
    
    # Get dashboard stats with appropriate shop filtering
    return get_dashboard_stats(db, shop_id)


@router.get("/shop-dashboard/{shop_id}", response_model=DashboardSummary)
def get_shop_dashboard(
    shop_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics for a specific shop
    - For superadmins/admins: Can view any shop's dashboard
    - For logist users: Can only view their assigned shop's dashboard
    """
    # Check if user has access to this shop's dashboard
    if current_user.role == UserRole.LOGIST:
        # Logist users can only see their assigned shop's dashboard
        if not current_user.shop_id or current_user.shop_id != shop_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this shop's dashboard"
            )
    elif current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        # Other roles don't have access
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access dashboard"
        )
    
    # Get shop-specific dashboard stats
    return get_dashboard_stats(db, shop_id)


# Banner management
@router.get("/banners", response_model=List[BannerResponse])
def read_banners(
    is_active: bool = None,
    position: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all banners
    """
    check_admin_access(current_user)
    
    if is_active:
        banners = get_active_banners(db, position)
    else:
        # Get all banners
        banners = db.query(Banner).all()
        if position:
            banners = [b for b in banners if b.position == position]
    
    return banners


@router.post("/banners", response_model=BannerResponse, status_code=status.HTTP_201_CREATED)
async def create_banner_endpoint(
    title: str = Form(...),
    subtitle: Optional[str] = Form(None),
    link_url: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    is_active: bool = Form(True),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new banner
    """
    check_admin_access(current_user)
    
    # Save banner image
    filename = await save_upload_file(image, "banners")
    image_url = f"/uploads/banners/{filename}"
    
    # Create banner
    banner_data = {
        "title": title,
        "subtitle": subtitle,
        "image_url": image_url,
        "link_url": link_url,
        "position": position,
        "is_active": is_active
    }
    
    # Add dates if provided
    if start_date:
        banner_data["start_date"] = start_date
    if end_date:
        banner_data["end_date"] = end_date
    
    banner = BannerCreate(**banner_data)
    return create_banner(db, banner)


@router.put("/banners/{banner_id}", response_model=BannerResponse)
async def update_banner_endpoint(
    banner_id: uuid.UUID,
    title: Optional[str] = Form(None),
    subtitle: Optional[str] = Form(None),
    link_url: Optional[str] = Form(None),
    position: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a banner
    """
    check_admin_access(current_user)
    
    # Check if banner exists
    banner = get_banner(db, banner_id)
    if not banner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
    
    # Prepare update data
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if subtitle is not None:
        update_data["subtitle"] = subtitle
    if link_url is not None:
        update_data["link_url"] = link_url
    if position is not None:
        update_data["position"] = position
    if is_active is not None:
        update_data["is_active"] = is_active
    if start_date is not None:
        update_data["start_date"] = start_date
    if end_date is not None:
        update_data["end_date"] = end_date
    
    # Handle image upload if provided
    if image:
        filename = await save_upload_file(image, "banners")
        image_url = f"/uploads/banners/{filename}"
        update_data["image_url"] = image_url
    
    banner_update = BannerUpdate(**update_data)
    return update_banner(db, banner_id, banner_update)


@router.delete("/banners/{banner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_banner_endpoint(
    banner_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a banner
    """
    check_admin_access(current_user)
    
    success = delete_banner(db, banner_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Banner not found")
    
    return None


# System settings
@router.get("/settings", response_model=List[SystemSettingResponse])
def read_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all system settings
    """
    check_admin_access(current_user)
    return get_all_system_settings(db)


@router.get("/settings/{key}", response_model=SystemSettingResponse)
def read_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific setting
    """
    check_admin_access(current_user)
    
    setting = get_system_setting(db, key)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Setting {key} not found")
    
    return setting


@router.put("/settings/{key}", response_model=SystemSettingResponse)
def update_setting(
    key: str,
    setting: SystemSettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a system setting
    """
    check_admin_access(current_user)
    return update_system_setting(db, key, setting)


# Reports
@router.get("/reports", response_model=List[ReportResponse])
def read_reports_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all reports
    """
    check_admin_access(current_user)
    return get_reports(db, skip, limit)


@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report_endpoint(
    report: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new report
    """
    check_admin_access(current_user)
    return create_report(db, report, current_user.id)


@router.get("/reports/{report_id}", response_model=ReportResponse)
def read_report_endpoint(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific report
    """
    check_admin_access(current_user)
    
    report = get_report(db, report_id)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    return report


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report_endpoint(
    report_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a report
    """
    check_admin_access(current_user)
    
    success = delete_report(db, report_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    return None


# Order management
@router.get("/orders", response_model=List[Dict[str, Any]])
def read_admin_orders(
    order_status: Optional[OrderStatus] = None,
    shop_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all orders (admin view)
    - For superadmins: Can view all orders or filter by shop_id
    - For logist users: Can only view orders for their assigned shop
    """
    # Handle access control based on user role
    if current_user.role == UserRole.LOGIST:
        # Logist users can only see their assigned shop's orders
        if not current_user.shop_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to any shop"
            )
        # Force the shop_id parameter to be the logist's assigned shop
        shop_id = current_user.shop_id
    elif current_user.role not in [UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access orders"
        )
    
    # Query orders with user information
    query = (
        db.query(Order, User.email)
        .join(User, Order.user_id == User.id)
    )
    
    # Filter by shop_id if provided
    if shop_id:
        # Join with order items and shop products to filter by shop
        from app.models.order import OrderItem
        from app.models.shop_product import ShopProduct
        query = query.join(OrderItem, Order.id == OrderItem.order_id)
        query = query.join(ShopProduct, OrderItem.shop_product_id == ShopProduct.id)
        query = query.filter(ShopProduct.shop_id == shop_id)
        query = query.distinct()
    
    if order_status:
        query = query.filter(Order.status == order_status)
    
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    results = query.all()
    
    # Format results
    orders = []
    for order, email in results:
        orders.append({
            "id": str(order.id),
            "order_number": order.order_number,
            "user_id": str(order.user_id),
            "user_email": email,
            "total_amount": order.total_amount,
            "status": order.status,
            "payment_status": order.payment_status,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        })
    
    return orders


@router.put("/orders/{order_id}/status", response_model=Dict[str, Any])
def update_order_status_endpoint(
    order_id: uuid.UUID,
    status: OrderStatus,
    comment: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update order status
    """
    check_admin_access(current_user)
    
    order = update_order_status(db, order_id, status, comment)
    return {
        "id": str(order.id),
        "order_number": order.order_number,
        "status": order.status,
        "updated_at": order.updated_at
    }


@router.put("/orders/{order_id}/payment", response_model=Dict[str, Any])
def update_order_payment_status_endpoint(
    order_id: uuid.UUID,
    payment_status: PaymentStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update order payment status
    """
    check_admin_access(current_user)
    
    order = update_payment_status(db, order_id, payment_status)
    return {
        "id": str(order.id),
        "order_number": order.order_number,
        "payment_status": order.payment_status,
        "updated_at": order.updated_at
    }


@router.put("/orders/{order_id}/shipping", response_model=Dict[str, Any])
def update_order_shipping_info_endpoint(
    order_id: uuid.UUID,
    tracking_number: str,
    shipping_company: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update order shipping information
    """
    check_admin_access(current_user)
    
    order = update_shipping_info(db, order_id, tracking_number, shipping_company)
    return {
        "id": str(order.id),
        "order_number": order.order_number,
        "status": order.status,
        "tracking_number": order.tracking_number,
        "shipping_company": order.shipping_company,
        "updated_at": order.updated_at
    }