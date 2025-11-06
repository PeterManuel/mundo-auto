from typing import List, Optional, Dict
import uuid

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.shop_product import ShopProduct
from app.models.product import Product, Category
from app.models.shop import Shop
from app.schemas.shop_product import ShopProductCreate, ShopProductUpdate


def get_shop_product(db: Session, shop_product_id: uuid.UUID) -> Optional[ShopProduct]:
    """Get shop product by ID"""
    return db.query(ShopProduct).filter(ShopProduct.id == shop_product_id).first()


def get_shop_product_by_shop_and_product(
    db: Session, shop_id: uuid.UUID, product_id: uuid.UUID
) -> Optional[ShopProduct]:
    """Get shop product by shop ID and product ID"""
    return db.query(ShopProduct).filter(
        ShopProduct.shop_id == shop_id,
        ShopProduct.product_id == product_id
    ).first()


def get_shop_products(
    db: Session,
    shop_id: Optional[uuid.UUID] = None,
    shop_name: Optional[str] = None,
    product_id: Optional[uuid.UUID] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    manufacturer_year: Optional[int] = None,
    oe_number: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    in_stock: Optional[bool] = None
) -> List[ShopProduct]:
    """
    Get shop products with various filters
    
    Args:
        db: Database session
        shop_id: Filter by specific shop ID
        shop_name: Filter by shop name (partial match)
        product_id: Filter by specific product
        category: Filter by category name (partial match)
        brand: Filter by product brand
        manufacturer: Filter by product manufacturer
        oe_number: Filter by product OE number
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        in_stock: Filter by stock availability
    """
    # Start with a join to include product, shop, and category information
    query = (
        db.query(ShopProduct)
        .join(ShopProduct.product)  # Join with Product (inner join as this is required)
        .join(ShopProduct.shop)     # Join with Shop (inner join as this is required)
        .outerjoin(Product.categories)   # Left join with Categories as they are optional
    )
    
    # Apply filters
    if shop_id:
        query = query.filter(ShopProduct.shop_id == shop_id)
    
    if shop_name:
        query = query.filter(Shop.name.ilike(f"%{shop_name}%"))
    
    if product_id:
        query = query.filter(ShopProduct.product_id == product_id)
    
    if category:
        # When filtering by category, make sure to handle NULL cases for products without categories
        query = query.filter(Category.name.ilike(f"%{category}%") if category else True)
    
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    
    if manufacturer:
        query = query.filter(Product.manufacturer.ilike(f"%{manufacturer}%"))
    
    if oe_number:
        query = query.filter(Product.oe_number.ilike(f"%{oe_number}%"))
    
    if model:
        query = query.filter(Product.model.ilike(f"%{model}%"))
    
    if manufacturer_year:
        query = query.filter(Product.manufacturer_year == manufacturer_year)
    
    if is_active is not None:
        query = query.filter(ShopProduct.is_active == is_active)
    
    if in_stock is not None:
        if in_stock:
            query = query.filter(ShopProduct.stock_quantity > 0)
        else:
            query = query.filter(ShopProduct.stock_quantity <= 0)
    
    return query.offset(skip).limit(limit).all()


def create_shop_product(
    db: Session, shop_product: ShopProductCreate
) -> ShopProduct:
    """
    Create a new shop product
    """
    # Check if product already exists for this shop
    existing = get_shop_product_by_shop_and_product(
        db, shop_product.shop_id, shop_product.product_id
    )
    
    if existing:
        # Product already exists for this shop, update instead
        existing.stock_quantity += shop_product.stock_quantity
        if shop_product.price:
            existing.price = shop_product.price
        if shop_product.sale_price:
            existing.sale_price = shop_product.sale_price
        if shop_product.sku:
            existing.sku = shop_product.sku
        
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new shop product
    db_shop_product = ShopProduct(**shop_product.dict())
    db.add(db_shop_product)
    db.commit()
    db.refresh(db_shop_product)
    return db_shop_product


def update_shop_product(
    db: Session, shop_product_id: uuid.UUID, shop_product: ShopProductUpdate
) -> Optional[ShopProduct]:
    """
    Update a shop product
    """
    db_shop_product = get_shop_product(db, shop_product_id)
    if not db_shop_product:
        return None
    
    # Update shop product attributes
    update_data = shop_product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_shop_product, key, value)
    
    db.add(db_shop_product)
    db.commit()
    db.refresh(db_shop_product)
    return db_shop_product


def delete_shop_product(db: Session, shop_product_id: uuid.UUID) -> bool:
    """
    Delete a shop product
    """
    db_shop_product = get_shop_product(db, shop_product_id)
    if not db_shop_product:
        return False
    
    db.delete(db_shop_product)
    db.commit()
    return True


def update_stock(db: Session, shop_product_id: uuid.UUID, quantity_change: int) -> Optional[ShopProduct]:
    """
    Update stock quantity for a shop product
    """
    db_shop_product = get_shop_product(db, shop_product_id)
    if not db_shop_product:
        return None
    
    # Update stock quantity
    db_shop_product.stock_quantity += quantity_change
    
    # Ensure stock doesn't go negative
    if db_shop_product.stock_quantity < 0:
        db_shop_product.stock_quantity = 0
    
    db.add(db_shop_product)
    db.commit()
    db.refresh(db_shop_product)
    return db_shop_product


def get_products_by_shops(db: Session, product_id: uuid.UUID) -> List[Dict]:
    """
    Get all shops that have a specific product and their respective stock information
    """
    result = []
    
    # Query for shop products of this product
    shop_products = db.query(ShopProduct).filter(
        ShopProduct.product_id == product_id,
        ShopProduct.is_active == True
    ).all()
    
    for sp in shop_products:
        shop = db.query(Shop).filter(Shop.id == sp.shop_id).first()
        if shop:
            result.append({
                "shop_id": shop.id,
                "shop_name": shop.name,
                "stock_quantity": sp.stock_quantity,
                "price": sp.price,
                "sale_price": sp.sale_price
            })
    
    return result


def get_all_brands(db: Session) -> List[str]:
    """
    Get all unique brands from active products in shops
    """
    query = (
        db.query(Product.brand)
        .join(ShopProduct)
        .filter(
            ShopProduct.is_active == True,
            Product.brand.isnot(None)  # Exclude null brands
        )
        .distinct()
        .order_by(Product.brand)
    )
    return [brand[0] for brand in query.all() if brand[0]]  # Remove any empty strings


def get_all_models(db: Session, brand: Optional[str] = None) -> List[str]:
    """
    Get all unique models from active products in shops
    
    Args:
        db: Database session
        brand: Optional brand name to filter models by
    """
    query = (
        db.query(Product.model)
        .join(ShopProduct)
        .filter(
            ShopProduct.is_active == True,
            Product.model.isnot(None)  # Exclude null models
        )
    )
    
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    
    query = query.distinct().order_by(Product.model)
    return [model[0] for model in query.all() if model[0]]  # Remove any empty strings