from typing import List, Optional, Dict
import uuid

from sqlalchemy.orm import Session

from app.models.cart import CartItem


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


def get_cart_item_by_shop_product(db: Session, shop_product_id: uuid.UUID, user_id: uuid.UUID) -> Optional[CartItem]:
    return (
        db.query(CartItem)
        .filter(CartItem.shop_product_id == shop_product_id, CartItem.user_id == user_id)
        .first()
    )


# This function is no longer needed since we work directly with shop_products
# def get_cart_item_by_product_and_shop(db: Session, product_id: uuid.UUID, shop_id: uuid.UUID, user_id: uuid.UUID) -> Optional[CartItem]:
#     """Get cart item by product ID, shop ID, and user ID"""
#     return (
#         db.query(CartItem)
#         .filter(
#             CartItem.product_id == product_id,
#             CartItem.shop_id == shop_id,
#             CartItem.user_id == user_id
#         )
#         .first()
#     )


def add_to_cart(db: Session, user_id: uuid.UUID, shop_product_id: uuid.UUID, quantity: int) -> CartItem:
    # Check if shop_product already in cart
    existing_item = get_cart_item_by_shop_product(db, shop_product_id, user_id)
    if existing_item:
        existing_item.quantity += quantity
        db.add(existing_item)
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        cart_item = CartItem(
            user_id=user_id,
            shop_product_id=shop_product_id,
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

    # Build CartItemResponse for each item
    items = []
    for cart_item in cart_items:
        shop_product = cart_item.shop_product
        shop = shop_product.shop
        items.append({
            "id": cart_item.id,
            "user_id": cart_item.user_id,
            "shop_product_id": shop_product.id,
            "quantity": cart_item.quantity,
            "created_at": cart_item.created_at,
            "updated_at": cart_item.updated_at,
            "product_name": shop_product.name,
            "product_price": shop_product.sale_price if shop_product.sale_price else shop_product.price,
            "total_price": cart_item.total_price,
            "product_image": shop_product.image,
            "shop_name": shop.name
        })

    return {
        "items": items,
        "total_items": total_items,
        "subtotal": subtotal,
    }