from typing import List, Optional
import uuid
from slugify import slugify

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.product import Category, Product, ProductImage, ProductReview
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
    
    # Always set parent_id to None for flat category structure
    # This ignores any parent_id that might be provided
    
    db_category = Category(
        name=category.name,
        slug=category.slug,
        description=category.description,
        parent_id=None,  # Always None for flat category structure
        image=category.image,
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
    
    # Ensure parent_id is always None in updates
    if "parent_id" in update_data:
        update_data.pop("parent_id")
    
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
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
    
    if oe_number:
        query = query.filter(Product.oe_number == oe_number)
    
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            (Product.name.ilike(search_term)) | 
            (Product.description.ilike(search_term)) | 
            (Product.oe_number.ilike(search_term))
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


# Product Image CRUD
def add_product_image(
    db: Session, product_id: uuid.UUID, image_url: str, alt_text: Optional[str] = None, is_primary: bool = False
) -> ProductImage:
    # If this is set as primary, unset other primary images
    if is_primary:
        db.query(ProductImage).filter(
            ProductImage.product_id == product_id, 
            ProductImage.is_primary == True
        ).update({"is_primary": False})
    
    db_image = ProductImage(
        product_id=product_id,
        image_url=image_url,
        alt_text=alt_text,
        is_primary=is_primary
    )
    
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def delete_product_image(db: Session, image_id: uuid.UUID) -> bool:
    db_image = db.query(ProductImage).filter(ProductImage.id == image_id).first()
    if not db_image:
        return False
    
    db.delete(db_image)
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