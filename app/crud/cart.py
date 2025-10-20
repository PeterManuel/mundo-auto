from typing import List, Optional, Dict
import uuid

from sqlalchemy.orm import Session

from app.models.cart import CartItem
from app.models.product import Product


def get_cart_items(db: Session, user_id: uuid.UUID) -> List[CartItem]:
    return (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .all()
    )


def get_cart_item(db: Session, cart_item_id: uuid.UUID, user_id: uuid.UUID) -> Optional[CartItem]:
    return (
        db.query(CartItem)
        .filter(CartItem.id == cart_item_id, CartItem.user_id == user_id)
        .first()
    )


def get_cart_item_by_product(db: Session, product_id: uuid.UUID, user_id: uuid.UUID) -> Optional[CartItem]:
    return (
        db.query(CartItem)
        .filter(CartItem.product_id == product_id, CartItem.user_id == user_id)
        .first()
    )


def add_to_cart(db: Session, user_id: uuid.UUID, product_id: uuid.UUID, quantity: int) -> CartItem:
    # Check if product already in cart
    existing_item = get_cart_item_by_product(db, product_id, user_id)
    
    if existing_item:
        # Update quantity
        existing_item.quantity += quantity
        db.add(existing_item)
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # Create new cart item
        cart_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )
        db.add(cart_item)
        db.commit()
        db.refresh(cart_item)
        return cart_item


def update_cart_item(db: Session, cart_item_id: uuid.UUID, user_id: uuid.UUID, quantity: int) -> Optional[CartItem]:
    cart_item = get_cart_item(db, cart_item_id, user_id)
    
    if not cart_item:
        return None
    
    cart_item.quantity = quantity
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


def remove_from_cart(db: Session, cart_item_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    cart_item = get_cart_item(db, cart_item_id, user_id)
    
    if not cart_item:
        return False
    
    db.delete(cart_item)
    db.commit()
    return True


def clear_cart(db: Session, user_id: uuid.UUID) -> bool:
    cart_items = get_cart_items(db, user_id)
    
    for item in cart_items:
        db.delete(item)
    
    db.commit()
    return True


def get_cart_summary(db: Session, user_id: uuid.UUID) -> Dict:
    cart_items = get_cart_items(db, user_id)
    
    total_items = sum(item.quantity for item in cart_items)
    subtotal = sum(item.total_price for item in cart_items)
    
    return {
        "items": cart_items,
        "total_items": total_items,
        "subtotal": subtotal,
    }