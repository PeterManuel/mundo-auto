from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud.product import (
    get_product,
    get_product_by_slug,
    get_products,
    create_product,
    update_product,
    delete_product,
    get_category,
    get_categories,
    create_category,
    update_category,
    delete_category,
    add_product_image,
    delete_product_image,
    create_product_review,
    get_product_reviews
)
from app.crud.shop_product import (
    get_shop_products,
    get_products_by_shops
)
from app.db.session import get_db
from app.models.user import User
from app.models.product import Category, Product
from app.schemas.product import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithSubcategories,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductWithShopInfoResponse,
    ProductReviewCreate,
    ProductReviewResponse
)
from app.utils.file_upload import save_upload_file

router = APIRouter()

# Category endpoints
@router.get("/categories/", response_model=List[CategoryResponse])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Get all categories or categories with specific parent
    """
    categories = get_categories(db, skip=skip, limit=limit, parent_id=parent_id)
    return categories


@router.get("/categories/{category_id_or_slug}", response_model=CategoryWithSubcategories)
def read_category(
    category_id_or_slug: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific category by ID or slug
    """
    # Check if it's a UUID or a slug
    try:
        category_id = uuid.UUID(category_id_or_slug)
        category = get_category(db, category_id=category_id)
    except ValueError:
        # Not a valid UUID, try as slug
        category = db.query(Category).filter(Category.slug == category_id_or_slug).first()
    
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    # Convert to dict and ensure subcategories is a list
    category_dict = {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "parent_id": category.parent_id,
        "image": category.image,
        "is_active": category.is_active,
        "created_at": category.created_at,
        "subcategories": []  # Initialize as empty list since we're using flat category structure
    }
    
    return category_dict


@router.post("/categories/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category_endpoint(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new category (admin only)
    Image must be a base64-encoded string.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    try:
        return create_category(db, category)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category_endpoint(
    category_id: uuid.UUID,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a category (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    db_category = update_category(db, category_id, category)
    if db_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    return db_category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category_endpoint(
    category_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a category (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    success = delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    return None


# Product endpoints
@router.get("/", response_model=List[ProductResponse])
def read_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[uuid.UUID] = None,
    brand: Optional[str] = None,
    model: Optional[str] = None,
    manufacturer_year: Optional[int] = None,
    oe_number: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_on_sale: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    compatible_vehicle: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get products with filtering options
    """
    products = get_products(
        db, 
        skip=skip, 
        limit=limit,
        category_id=category_id,
        brand=brand,
        model=model,
        manufacturer_year=manufacturer_year,
        oe_number=oe_number,
        search_query=search,
        min_price=min_price,
        max_price=max_price,
        is_on_sale=is_on_sale,
        is_featured=is_featured,
        compatible_vehicle=compatible_vehicle
    )
    
    return products


@router.get("/brands", response_model=List[str])
def read_brands(db: Session = Depends(get_db)):
    """
    Get all unique brands
    """
    # Query distinct brands
    brands = db.query(Product.brand).distinct().filter(Product.brand.isnot(None)).all()
    return [brand[0] for brand in brands if brand[0]]


@router.get("/{product_id_or_slug}", response_model=ProductWithShopInfoResponse)
def read_product(
    product_id_or_slug: str,
    shop_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db)
):
    """
    Get a specific product by ID or slug with shop inventory information
    """
    # Check if it's a UUID or a slug
    try:
        product_id = uuid.UUID(product_id_or_slug)
        product = get_product(db, product_id=product_id)
    except ValueError:
        # Not a valid UUID, try as slug
        product = get_product_by_slug(db, slug=product_id_or_slug)
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    # Get shop information for this product
    shop_info = get_products_by_shops(db, product.id)
    
    # Create response
    response_dict = {
        **product.__dict__,
        "shop_info": shop_info
    }
    
    return response_dict
    
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product_endpoint(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new product (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return create_product(db, product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product_endpoint(
    product_id: uuid.UUID,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a product (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    db_product = update_product(db, product_id, product)
    if db_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_endpoint(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a product (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    success = delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return None


@router.post("/{product_id}/images", status_code=status.HTTP_201_CREATED)
def upload_product_image_base64(
    product_id: uuid.UUID,
    image_data: str,
    is_primary: bool = False,
    alt_text: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload product image as base64 string (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    # Check if product exists
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    # Add image to product
    image = add_product_image(db, product_id, image_data, alt_text, is_primary)
    return {"id": image.id, "is_primary": image.is_primary}


@router.delete("/{product_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_image_endpoint(
    product_id: uuid.UUID,
    image_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete product image (admin only)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    success = delete_product_image(db, image_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
    
    return None


@router.post("/{product_id}/reviews", response_model=ProductReviewResponse)
def create_product_review_endpoint(
    product_id: uuid.UUID,
    review: ProductReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a product review
    """
    # Check if product exists
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    # Create review
    return create_product_review(
        db, 
        product_id=product_id,
        user_id=current_user.id,
        rating=review.rating,
        comment=review.comment
    )


@router.get("/{product_id}/reviews", response_model=List[ProductReviewResponse])
def read_product_reviews_endpoint(
    product_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get reviews for a product
    """
    # Check if product exists
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return get_product_reviews(db, product_id, skip, limit)