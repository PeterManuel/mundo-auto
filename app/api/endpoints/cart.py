from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud.cart import (
    get_cart_items,
    get_cart_item,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    clear_cart,
    get_cart_summary
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartItemResponse, CartSummaryResponse

router = APIRouter()


@router.get("/", response_model=CartSummaryResponse)
def read_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's cart
    """
    cart_summary = get_cart_summary(db, current_user.id)
    return cart_summary


@router.post("/", response_model=CartItemResponse)
def add_item_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add item to cart
    """
    cart_item = add_to_cart(db, current_user.id, item.shop_product_id, item.quantity)

    shop_product = cart_item.shop_product
    product = shop_product.product
    shop = shop_product.shop

    response = CartItemResponse(
        id=cart_item.id,
        user_id=cart_item.user_id,
        shop_product_id=shop_product.id,
        quantity=cart_item.quantity,
        created_at=cart_item.created_at,
        updated_at=cart_item.updated_at,
        product_name=product.name,
        product_price=shop_product.sale_price if shop_product.sale_price else shop_product.price if shop_product.price is not None else (product.sale_price if product.sale_price else product.price),
        total_price=cart_item.total_price,
        product_image=product.images[0].image_url if product.images else None,
        shop_name=shop.name
    )
    return response


@router.put("/{cart_item_id}", response_model=CartItemResponse)
def update_item_in_cart(
    cart_item_id: uuid.UUID,
    item: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update item quantity in cart
    """
    cart_item = update_cart_item(db, cart_item_id, current_user.id, item.quantity)
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart")

    shop_product = cart_item.shop_product
    product = shop_product.product
    shop = shop_product.shop

    response = CartItemResponse(
        id=cart_item.id,
        user_id=cart_item.user_id,
        shop_product_id=shop_product.id,
        quantity=cart_item.quantity,
        created_at=cart_item.created_at,
        updated_at=cart_item.updated_at,
        product_name=product.name,
        product_price=shop_product.sale_price if shop_product.sale_price else shop_product.price if shop_product.price is not None else (product.sale_price if product.sale_price else product.price),
        total_price=cart_item.total_price,
        product_image=product.images[0].image_url if product.images else None,
        shop_name=shop.name
    )
    return response


@router.delete("/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_from_cart(
    cart_item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove item from cart
    """
    success = remove_from_cart(db, cart_item_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found in cart")
    
    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_user_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clear the entire cart
    """
    clear_cart(db, current_user.id)
    return None