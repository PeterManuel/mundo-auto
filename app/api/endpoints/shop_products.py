from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud.shop_product import (
    get_shop_product,
    get_shop_products,
    create_shop_product,
    update_shop_product,
    delete_shop_product,
    update_stock,
    get_products_by_shops,
    get_all_brands,
    get_all_models
)
from app.crud.shop import get_shop
from app.crud.product import get_product
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.shop_product import (
    ShopProductCreate,
    ShopProductUpdate,
    ShopProductResponse,
    ShopProductFullResponse
)

router = APIRouter()


@router.get("/brands", response_model=List[str], status_code=status.HTTP_200_OK)
async def get_brands(
    db: Session = Depends(get_db)
) -> List[str]:
    """
    Get all unique brands from active products in shops
    """
    return get_all_brands(db)


@router.get("/models", response_model=List[str], status_code=status.HTTP_200_OK)
async def get_models(
    brand: Optional[str] = Query(None, description="Filter models by brand name"),
    db: Session = Depends(get_db)
) -> List[str]:
    """
    Get all unique models from active products in shops.
    Optionally filter by brand name.
    """
    return get_all_models(db, brand)


# Helper function to check user's shop access
def check_shop_access(current_user: User, shop_id: uuid.UUID) -> bool:
    """
    Check if user has access to the shop
    """
    # Superadmin has access to all shops
    if current_user.role == UserRole.SUPERADMIN:
        return True
    
    # Logist has access only to their assigned shop
    if current_user.role == UserRole.LOGIST:
        return str(current_user.shop_id) == str(shop_id)
    
    # Other users don't have access
    return False


@router.get("/", response_model=List[ShopProductFullResponse])
def read_shop_products(
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
    in_stock: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get shop products with various filters
    
    - **shop_id**: Filter by specific shop ID
    - **shop_name**: Filter by shop name (partial match)
    - **product_id**: Filter by specific product
    - **category**: Filter by category name (partial match)
    - **brand**: Filter by product brand
    - **manufacturer**: Filter by product manufacturer
    - **model**: Filter by vehicle model (partial match)
    - **manufacturer_year**: Filter by vehicle manufacturer year
    - **oe_number**: Filter by product OE number
    - **is_active**: Filter by active status
    - **in_stock**: Filter by stock availability
    """
    shop_products = get_shop_products(
        db,
        shop_id=shop_id,
        shop_name=shop_name,
        product_id=product_id,
        category=category,
        brand=brand,
        manufacturer=manufacturer,
        model=model,
        manufacturer_year=manufacturer_year,
        oe_number=oe_number,
        skip=skip,
        limit=limit,
        is_active=is_active,
        in_stock=in_stock
    )
    
    # Prepare response with product and shop information
    result = []
    for sp in shop_products:
        product = sp.product
        shop = sp.shop
        product_images = [img.image_url for img in product.images]
        product_categories = [category.name for category in product.categories]
        
        result.append(
            ShopProductFullResponse(
                id=sp.id,
                shop_id=sp.shop_id,
                product_id=sp.product_id,
                stock_quantity=sp.stock_quantity,
                price=sp.price or product.price,
                sale_price=sp.sale_price or product.sale_price,
                sku=sp.sku or product.sku,
                is_active=sp.is_active,
                created_at=sp.created_at,
                updated_at=sp.updated_at,
                product_name=product.name,
                product_description=product.description,
                shop_name=shop.name,
                product_images=product_images,
                model=product.model,
                manufacturer_year=product.manufacturer_year,
                product_categories=product_categories,
                manufacturer=product.manufacturer
            )
        )
    
    return result


@router.get("/{shop_product_id}", response_model=ShopProductFullResponse)
def read_shop_product(
    shop_product_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific shop product
    """
    shop_product = get_shop_product(db, shop_product_id)
    if not shop_product:
        raise HTTPException(status_code=404, detail="Shop product not found")
    
    product = shop_product.product
    shop = shop_product.shop
    
    # Get product images
    product_images = []
    if product.images:
        product_images = [image.image_url for image in product.images]
    
    # Get product categories
    product_categories = []
    if product.categories:
        product_categories = [category.name for category in product.categories]
    
    # Prepare full response
    response = ShopProductFullResponse(
        id=shop_product.id,
        shop_id=shop_product.shop_id,
        product_id=shop_product.product_id,
        stock_quantity=shop_product.stock_quantity,
        price=shop_product.price or product.price,
        sale_price=shop_product.sale_price or product.sale_price,
        sku=shop_product.sku or product.sku,
        is_active=shop_product.is_active,
        created_at=shop_product.created_at,
        updated_at=shop_product.updated_at,
        product_name=product.name,
        product_description=product.description,
        shop_name=shop.name,
        product_images=product_images,
        product_categories=product_categories,
        manufacturer=product.manufacturer
    )
    
    return response


@router.post("/", response_model=ShopProductFullResponse, status_code=status.HTTP_201_CREATED)
def create_shop_product_endpoint(
    shop_product: ShopProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new shop product
    """
    # Check if user has access to the shop
    if not check_shop_access(current_user, shop_product.shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage products for this shop"
        )
    
    # Verify shop exists
    shop = get_shop(db, shop_product.shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Verify product exists
    product = get_product(db, shop_product.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create shop product
    db_shop_product = create_shop_product(db, shop_product)
    
    # Get product images and categories
    product_images = [img.image_url for img in product.images]
    product_categories = [category.name for category in product.categories]
    
    # Prepare response with product and shop information
    response = ShopProductFullResponse(
        id=db_shop_product.id,
        shop_id=db_shop_product.shop_id,
        product_id=db_shop_product.product_id,
        stock_quantity=db_shop_product.stock_quantity,
        price=db_shop_product.price or product.price,
        sale_price=db_shop_product.sale_price or product.sale_price,
        sku=db_shop_product.sku or product.sku,
        is_active=db_shop_product.is_active,
        created_at=db_shop_product.created_at,
        updated_at=db_shop_product.updated_at,
        product_name=product.name,
        product_description=product.description,
        shop_name=shop.name,
        product_images=product_images,
        product_categories=product_categories
    )
    
    return response


@router.put("/{shop_product_id}", response_model=ShopProductFullResponse)
def update_shop_product_endpoint(
    shop_product_id: uuid.UUID,
    shop_product_update: ShopProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a shop product
    """
    # Get shop product
    db_shop_product = get_shop_product(db, shop_product_id)
    if not db_shop_product:
        raise HTTPException(status_code=404, detail="Shop product not found")
    
    # Check if user has access to the shop
    if not check_shop_access(current_user, db_shop_product.shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage products for this shop"
        )
    
    # Update shop product
    updated_shop_product = update_shop_product(db, shop_product_id, shop_product_update)
    if not updated_shop_product:
        raise HTTPException(status_code=404, detail="Shop product not found")
    
    # Get product information
    product = updated_shop_product.product
    
    # Prepare response with product information
    response = ShopProductResponse(
        id=updated_shop_product.id,
        shop_id=updated_shop_product.shop_id,
        product_id=updated_shop_product.product_id,
        stock_quantity=updated_shop_product.stock_quantity,
        price=updated_shop_product.price or product.price,
        sale_price=updated_shop_product.sale_price or product.sale_price,
        sku=updated_shop_product.sku or product.sku,
        is_active=updated_shop_product.is_active,
        created_at=updated_shop_product.created_at,
        updated_at=updated_shop_product.updated_at,
        product_name=product.name,
        product_description=product.description
    )
    
    return response


@router.delete("/{shop_product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shop_product_endpoint(
    shop_product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a shop product
    """
    # Get shop product
    db_shop_product = get_shop_product(db, shop_product_id)
    if not db_shop_product:
        raise HTTPException(status_code=404, detail="Shop product not found")
    
    # Check if user has access to the shop
    if not check_shop_access(current_user, db_shop_product.shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage products for this shop"
        )
    
    # Delete shop product
    success = delete_shop_product(db, shop_product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shop product not found")
    
    return


@router.put("/{shop_product_id}/stock", response_model=ShopProductResponse)
def update_stock_endpoint(
    shop_product_id: uuid.UUID,
    quantity_change: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update stock quantity for a shop product
    """
    # Get shop product
    db_shop_product = get_shop_product(db, shop_product_id)
    if not db_shop_product:
        raise HTTPException(status_code=404, detail="Shop product not found")
    
    # Check if user has access to the shop
    if not check_shop_access(current_user, db_shop_product.shop_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage products for this shop"
        )
    
    # Update stock quantity
    updated_shop_product = update_stock(db, shop_product_id, quantity_change)
    if not updated_shop_product:
        raise HTTPException(status_code=404, detail="Shop product not found")
    
    # Get product information
    product = updated_shop_product.product
    
    # Prepare response with product information
    response = ShopProductResponse(
        id=updated_shop_product.id,
        shop_id=updated_shop_product.shop_id,
        product_id=updated_shop_product.product_id,
        stock_quantity=updated_shop_product.stock_quantity,
        price=updated_shop_product.price or product.price,
        sale_price=updated_shop_product.sale_price or product.sale_price,
        sku=updated_shop_product.sku or product.sku,
        is_active=updated_shop_product.is_active,
        created_at=updated_shop_product.created_at,
        updated_at=updated_shop_product.updated_at,
        product_name=product.name,
        product_description=product.description
    )
    
    return response


@router.get("/product/{product_id}/shops", response_model=List[ShopProductResponse])
def get_product_shops_endpoint(
    product_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get all shops that have a specific product
    """
    # Get all shop products for this product
    shop_products = get_shop_products(db, product_id=product_id, is_active=True)
    
    # Prepare response with product and shop information
    result = []
    for sp in shop_products:
        product = sp.product
        result.append(
            ShopProductResponse(
                id=sp.id,
                shop_id=sp.shop_id,
                product_id=sp.product_id,
                stock_quantity=sp.stock_quantity,
                price=sp.price or product.price,
                sale_price=sp.sale_price or product.sale_price,
                sku=sp.sku or product.sku,
                is_active=sp.is_active,
                created_at=sp.created_at,
                updated_at=sp.updated_at,
                product_name=product.name,
                product_description=product.description
            )
        )
    
    return result