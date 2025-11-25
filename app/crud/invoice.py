from datetime import datetime, timedelta
from typing import Optional
import uuid

from sqlalchemy.orm import Session

from app.models.order import Order, PaymentStatus
from app.models.user import User
from app.models.shop import Shop
from app.models.shop_product import ShopProduct
from app.schemas.invoice import (
    InvoiceData, 
    InvoiceItemData, 
    InvoiceCustomerData, 
    InvoiceShopData
)


def generate_invoice_number(order_number: str) -> str:
    """Generate invoice number from order number"""
    return f"INV-{order_number.replace('ORD-', '')}"


def get_invoice_data(db: Session, order_id: uuid.UUID, shop_id: uuid.UUID) -> Optional[InvoiceData]:
    """
    Get invoice data for a paid order from a specific shop
    
    Args:
        db: Database session
        order_id: Order ID
        shop_id: Shop ID to verify order belongs to shop
        
    Returns:
        InvoiceData if order is paid and belongs to shop, None otherwise
    """
    # Get order with related data
    order = (
        db.query(Order)
        .join(Order.user)
        .join(Order.items)
        .filter(Order.id == order_id)
        .first()
    )
    
    if not order:
        return None
    
    # Check if order is paid
    if order.payment_status != PaymentStatus.PAID:
        return None
    
    # Check if order has items from the specified shop
    shop_items = []
    for item in order.items:
        # Get the shop_product to check shop_id
        shop_product = db.query(ShopProduct).filter(ShopProduct.id == item.shop_product_id).first()
        if shop_product and str(shop_product.shop_id) == str(shop_id):
            shop_items.append(item)
    
    if not shop_items:
        return None
    
    # Get shop information
    shop = db.query(Shop).filter(Shop.id == shop_id).first()
    if not shop:
        return None
    
    # Calculate financial details for shop items only
    subtotal = sum(item.price * item.quantity for item in shop_items)
    shipping_cost = 0.0  # You can implement shipping cost logic here
    tax_rate = 0.0  # You can implement tax logic here
    tax_amount = subtotal * tax_rate
    total_amount = subtotal + shipping_cost + tax_amount
    
    # Generate invoice number
    invoice_number = generate_invoice_number(order.order_number)
    
    # Create customer data
    customer_data = InvoiceCustomerData(
        customer_id=order.user.id,
        name=f"{order.user.first_name or ''} {order.user.last_name or ''}".strip() or "N/A",
        email=order.user.email,
        phone_number=order.user.phone_number
    )
    
    # Create shop data
    shop_data = InvoiceShopData(
        shop_id=shop.id,
        name=shop.name,
        address=shop.address,
        phone=shop.phone,
        email=shop.email,
        logo=shop.logo
    )
    
    # Create items data
    items_data = []
    for item in shop_items:
        # Get shop product for additional details
        shop_product = db.query(ShopProduct).filter(ShopProduct.id == item.shop_product_id).first()
        
        item_data = InvoiceItemData(
            product_name=item.product_name,
            quantity=item.quantity,
            unit_price=item.price,
            total_price=item.price * item.quantity,
            shop_name=item.shop_name,
            sku=shop_product.sku if shop_product else None,
            oe_number=shop_product.oe_number if shop_product else None,
            brand=shop_product.brand if shop_product else None
        )
        items_data.append(item_data)
    
    # Create invoice data
    invoice_data = InvoiceData(
        order_id=order.id,
        order_number=order.order_number,
        invoice_number=invoice_number,
        invoice_date=datetime.utcnow(),
        due_date=None,  # Immediate payment
        order_date=order.created_at,
        order_status=order.status,
        payment_method=order.payment_method,
        payment_status=order.payment_status,
        customer=customer_data,
        shop=shop_data,
        billing_address=order.billing_address,
        shipping_address=order.shipping_address,
        items=items_data,
        subtotal=subtotal,
        shipping_cost=shipping_cost,
        tax_amount=tax_amount,
        tax_rate=tax_rate,
        total_amount=total_amount,
        notes=order.notes,
        tracking_number=order.tracking_number,
        shipping_company=order.shipping_company
    )
    
    return invoice_data