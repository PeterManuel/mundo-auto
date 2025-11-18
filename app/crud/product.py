from typing import List, Optional
import uuid
from slugify import slugify

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product import Category, Product, ProductReview
from app.schemas.product import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate


# Category CRUD operations
def get_category(db: Session, category_id: uuid.UUID) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_slug(db: Session, slug: str) -> Optional[Category]:
    return db.query(Category).filter(Category.slug == slug).first()


def get_categories(
    db: Session, skip: int = 0, limit: int = 100, parent_id: Optional[uuid.UUID] = None
) -> List[Category]:
    # Since we're using a flat category structure, we ignore parent_id
    # and always return all categories (all will have parent_id=None)
    query = db.query(Category)
    
    return query.offset(skip).limit(limit).all()


def create_category(db: Session, category: CategoryCreate) -> Category:
    # Generate slug if not provided
    if not category.slug:
        category.slug = slugify(category.name)
    
    # Check if parent_id exists and is valid if provided
    parent_id = None
    if category.parent_id is not None:
        parent = get_category(db, category.parent_id)
        if not parent:
            raise ValueError("Parent category not found")
        parent_id = category.parent_id
    
    db_category = Category(
        name=category.name,
        slug=category.slug,
        description=category.description,
        parent_id=parent_id,
        image=category.image,  # base64 string
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(
    db: Session, category_id: uuid.UUID, category: CategoryUpdate
) -> Optional[Category]:
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    update_data = category.dict(exclude_unset=True)
    
    # Update slug if name is updated and slug is not provided
    if "name" in update_data and "slug" not in update_data:
        update_data["slug"] = slugify(update_data["name"])
    
    # Check if parent_id exists and is valid if provided
    if "parent_id" in update_data:
        if update_data["parent_id"] is not None:
            parent = get_category(db, update_data["parent_id"])
            if not parent:
                raise ValueError("Parent category not found")
        # If parent_id is None, it will remove the parent relationship
    
    for field, value in update_data.items():
        setattr(db_category, field, value)  # image is base64 string
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: uuid.UUID) -> bool:
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True


# Product CRUD operations
def get_product(db: Session, product_id: uuid.UUID) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()


def get_product_by_slug(db: Session, slug: str) -> Optional[Product]:
    return db.query(Product).filter(Product.slug == slug).first()


def get_products(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[uuid.UUID] = None,
    brand: Optional[str] = None,
    oe_number: Optional[str] = None,
    model: Optional[str] = None,
    manufacturer_year: Optional[int] = None,
    search_query: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_on_sale: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    compatible_vehicle: Optional[str] = None,
) -> List[Product]:
    query = db.query(Product).filter(Product.is_active == True)
    
    if category_id:
        query = query.join(Product.categories).filter(Category.id == category_id)
    
    if brand:
        query = query.filter(Product.brand == brand)
    
    if model:
        query = query.filter(Product.model == model)
    
    if manufacturer_year:
        query = query.filter(Product.manufacturer_year == manufacturer_year)
    
    if oe_number:
        query = query.filter(Product.oe_number == oe_number)
    
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            (Product.name.ilike(search_term)) | 
            (Product.description.ilike(search_term)) | 
            (Product.oe_number.ilike(search_term)) |
            (Product.model.ilike(search_term))
        )
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if is_on_sale is not None:
        query = query.filter(Product.is_on_sale == is_on_sale)
    
    if is_featured is not None:
        query = query.filter(Product.is_featured == is_featured)
    
    if compatible_vehicle:
        query = query.filter(Product.compatible_vehicles.any(compatible_vehicle))
    
    return query.offset(skip).limit(limit).all()


def create_product(db: Session, product: ProductCreate) -> Product:
    # Generate slug if not provided
    if not product.slug:
        product.slug = slugify(product.name)
    
    # Prepare product data
    product_data = product.dict(exclude={"category_ids", "slug"})
    db_product = Product(slug=product.slug, **product_data)
    
    # Add categories
    if product.category_ids:
        categories = db.query(Category).filter(Category.id.in_(product.category_ids)).all()
        db_product.categories = categories
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(
    db: Session, product_id: uuid.UUID, product: ProductUpdate
) -> Optional[Product]:
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    update_data = product.dict(exclude_unset=True, exclude={"category_ids"})
    
    # Update slug if name is updated
    if "name" in update_data:
        update_data["slug"] = slugify(update_data["name"])
    
    # Update product fields
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    # Update categories if provided
    if product.category_ids:
        categories = db.query(Category).filter(Category.id.in_(product.category_ids)).all()
        db_product.categories = categories
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: uuid.UUID) -> bool:
    db_product = get_product(db, product_id)
    if not db_product:
        return False
    
    db.delete(db_product)
    db.commit()
    return True


# Product Review CRUD
def create_product_review(
    db: Session, product_id: uuid.UUID, user_id: uuid.UUID, rating: int, comment: Optional[str] = None
) -> ProductReview:
    db_review = ProductReview(
        product_id=product_id,
        user_id=user_id,
        rating=rating,
        comment=comment
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def get_product_reviews(
    db: Session, product_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> List[ProductReview]:
    return (
        db.query(ProductReview)
        .filter(ProductReview.product_id == product_id)
        .order_by(ProductReview.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )