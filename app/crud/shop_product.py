from typing import List, Optional, Dict
import uuid
from slugify import slugify

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.shop_product import ShopProduct
from app.models.product import Category
from app.models.shop import Shop
from app.schemas.shop_product import ShopProductCreate, ShopProductUpdate


def get_shop_product(db: Session, shop_product_id: uuid.UUID) -> Optional[ShopProduct]:
    """Get shop product by ID"""
    return db.query(ShopProduct).filter(ShopProduct.id == shop_product_id).first()


def get_shop_product_by_shop_and_slug(
    db: Session, shop_id: uuid.UUID, slug: str
) -> Optional[ShopProduct]:
    """Get shop product by shop ID and slug"""
    return db.query(ShopProduct).filter(
        ShopProduct.shop_id == shop_id,
        ShopProduct.slug == slug
    ).first()


def get_shop_products(
    db: Session,
    shop_id: Optional[uuid.UUID] = None,
    shop_name: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    manufacturer_year: Optional[int] = None,
    oe_number: Optional[str] = None,
    search_query: Optional[str] = None,
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
        category: Filter by category name (partial match)
        brand: Filter by product brand
        manufacturer: Filter by product manufacturer
        model: Filter by vehicle model
        manufacturer_year: Filter by manufacturer year
        oe_number: Filter by product OE number
        search_query: Search in name, description, OE number, model
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
        in_stock: Filter by stock availability
    """
    # Start with a join to include shop and category information
    query = (
        db.query(ShopProduct)
        .join(ShopProduct.shop)     # Join with Shop (inner join as this is required)
        .outerjoin(ShopProduct.categories)   # Left join with Categories as they are optional
    )
    
    # Apply filters
    if shop_id:
        query = query.filter(ShopProduct.shop_id == shop_id)
    
    if shop_name:
        query = query.filter(Shop.name.ilike(f"%{shop_name}%"))
    
    if category:
        query = query.filter(Category.name.ilike(f"%{category}%"))
    
    if brand:
        query = query.filter(ShopProduct.brand.ilike(f"%{brand}%"))
    
    if manufacturer:
        query = query.filter(ShopProduct.manufacturer.ilike(f"%{manufacturer}%"))
    
    if oe_number:
        query = query.filter(ShopProduct.oe_number.ilike(f"%{oe_number}%"))
    
    if model:
        query = query.filter(ShopProduct.model.ilike(f"%{model}%"))
    
    if manufacturer_year:
        query = query.filter(ShopProduct.manufacturer_year == manufacturer_year)
    
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            (ShopProduct.name.ilike(search_term)) | 
            (ShopProduct.description.ilike(search_term)) | 
            (ShopProduct.oe_number.ilike(search_term)) |
            (ShopProduct.model.ilike(search_term))
        )
    
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
    # Generate slug if not provided
    if not shop_product.slug:
        base_slug = slugify(shop_product.name)
        # Ensure uniqueness within the shop
        counter = 1
        slug = base_slug
        while get_shop_product_by_shop_and_slug(db, shop_product.shop_id, slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        shop_product.slug = slug
    
    # Prepare shop product data
    product_data = shop_product.dict(exclude={"category_ids", "slug"})
    db_shop_product = ShopProduct(slug=shop_product.slug, **product_data)
    
    # Add categories
    if shop_product.category_ids:
        categories = db.query(Category).filter(Category.id.in_(shop_product.category_ids)).all()
        db_shop_product.categories = categories
    
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
    
    update_data = shop_product.dict(exclude_unset=True, exclude={"category_ids"})
    
    # Update slug if name is updated
    if "name" in update_data:
        base_slug = slugify(update_data["name"])
        # Ensure uniqueness within the shop (excluding current product)
        counter = 1
        slug = base_slug
        while True:
            existing = get_shop_product_by_shop_and_slug(db, db_shop_product.shop_id, slug)
            if not existing or existing.id == db_shop_product.id:
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
        update_data["slug"] = slug
    
    # Update shop product fields
    for field, value in update_data.items():
        setattr(db_shop_product, field, value)
    
    # Update categories if provided
    if shop_product.category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(shop_product.category_ids)).all()
        db_shop_product.categories = categories
    
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


def get_shop_products_by_name_or_oe(db: Session, name: Optional[str] = None, oe_number: Optional[str] = None) -> List[Dict]:
    """
    Get all shop products that match a specific name or OE number with shop information
    """
    result = []
    
    query = db.query(ShopProduct).filter(ShopProduct.is_active == True)
    
    if name:
        query = query.filter(ShopProduct.name.ilike(f"%{name}%"))
    
    if oe_number:
        query = query.filter(ShopProduct.oe_number == oe_number)
    
    shop_products = query.all()
    
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
    Get all unique brands from active shop products
    """
    query = (
        db.query(ShopProduct.brand)
        .filter(
            ShopProduct.is_active == True,
            ShopProduct.brand.isnot(None)  # Exclude null brands
        )
        .distinct()
        .order_by(ShopProduct.brand)
    )
    return [brand[0] for brand in query.all() if brand[0]]  # Remove any empty strings


def get_all_models(db: Session, brand: Optional[str] = None) -> List[str]:
    """
    Get all unique models from active shop products
    
    Args:
        db: Database session
        brand: Optional brand name to filter models by
    """
    query = (
        db.query(ShopProduct.model)
        .filter(
            ShopProduct.is_active == True,
            ShopProduct.model.isnot(None)  # Exclude null models
        )
    )
    
    if brand:
        query = query.filter(ShopProduct.brand.ilike(f"%{brand}%"))
    
    query = query.distinct().order_by(ShopProduct.model)
    return [model[0] for model in query.all() if model[0]]  # Remove any empty strings