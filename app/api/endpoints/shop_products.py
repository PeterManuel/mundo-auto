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
    get_shop_products_by_name_or_oe,
    get_all_brands,
    get_all_models
)
from app.crud.shop import get_shop
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
    category: Optional[str] = None,
    brand: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    manufacturer_year: Optional[int] = None,
    oe_number: Optional[str] = None,
    search: Optional[str] = None,
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
    - **category**: Filter by category name (partial match)
    - **brand**: Filter by product brand
    - **manufacturer**: Filter by product manufacturer
    - **model**: Filter by vehicle model (partial match)
    - **manufacturer_year**: Filter by vehicle manufacturer year
    - **oe_number**: Filter by product OE number
    - **search**: Search in name, description, OE number, model
    - **is_active**: Filter by active status
    - **in_stock**: Filter by stock availability
    """
    shop_products = get_shop_products(
        db,
        shop_id=shop_id,
        shop_name=shop_name,
        category=category,
        brand=brand,
        manufacturer=manufacturer,
        model=model,
        manufacturer_year=manufacturer_year,
        oe_number=oe_number,
        search_query=search,
        skip=skip,
        limit=limit,
        is_active=is_active,
        in_stock=in_stock
    )
    
    # Prepare response with shop information
    result = []
    for sp in shop_products:
        shop = sp.shop
        
        result.append(
            ShopProductFullResponse(
                id=sp.id,
                shop_id=sp.shop_id,
                name=sp.name,
                slug=sp.slug,
                description=sp.description,
                technical_details=sp.technical_details,
                price=sp.price,
                sale_price=sp.sale_price,
                sku=sp.sku,
                oe_number=sp.oe_number,
                brand=sp.brand,
                manufacturer=sp.manufacturer,
                model=sp.model,
                manufacturer_year=sp.manufacturer_year,
                compatible_vehicles=sp.compatible_vehicles,
                weight=sp.weight,
                dimensions=sp.dimensions,
                image=sp.image,
                is_featured=sp.is_featured,
                is_on_sale=sp.is_on_sale,
                stock_quantity=sp.stock_quantity,
                is_active=sp.is_active,
                created_at=sp.created_at,
                updated_at=sp.updated_at,
                categories=[{
                    "id": str(cat.id), 
                    "name": cat.name, 
                    "slug": cat.slug, 
                    "description": cat.description, 
                    "parent_id": str(cat.parent_id) if cat.parent_id else None, 
                    "image": cat.image, 
                    "is_active": cat.is_active, 
                    "created_at": cat.created_at.isoformat() if cat.created_at else None
                } for cat in sp.categories],
                shop_name=shop.name
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
    
    shop = shop_product.shop
    
    # Prepare full response
    response = ShopProductFullResponse(
        id=shop_product.id,
        shop_id=shop_product.shop_id,
        name=shop_product.name,
        slug=shop_product.slug,
        description=shop_product.description,
        technical_details=shop_product.technical_details,
        price=shop_product.price,
        sale_price=shop_product.sale_price,
        sku=shop_product.sku,
        oe_number=shop_product.oe_number,
        brand=shop_product.brand,
        manufacturer=shop_product.manufacturer,
        model=shop_product.model,
        manufacturer_year=shop_product.manufacturer_year,
        compatible_vehicles=shop_product.compatible_vehicles,
        weight=shop_product.weight,
        dimensions=shop_product.dimensions,
        image=shop_product.image,
        is_featured=shop_product.is_featured,
        is_on_sale=shop_product.is_on_sale,
        stock_quantity=shop_product.stock_quantity,
        is_active=shop_product.is_active,
        created_at=shop_product.created_at,
        updated_at=shop_product.updated_at,
        categories=[{
            "id": str(cat.id), 
            "name": cat.name, 
            "slug": cat.slug, 
            "description": cat.description, 
            "parent_id": str(cat.parent_id) if cat.parent_id else None, 
            "image": cat.image, 
            "is_active": cat.is_active, 
            "created_at": cat.created_at.isoformat() if cat.created_at else None
        } for cat in shop_product.categories],
        shop_name=shop.name
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
    
    # Create shop product
    db_shop_product = create_shop_product(db, shop_product)
    
    # Prepare response with shop information
    response = ShopProductFullResponse(
        id=db_shop_product.id,
        shop_id=db_shop_product.shop_id,
        name=db_shop_product.name,
        slug=db_shop_product.slug,
        description=db_shop_product.description,
        technical_details=db_shop_product.technical_details,
        price=db_shop_product.price,
        sale_price=db_shop_product.sale_price,
        sku=db_shop_product.sku,
        oe_number=db_shop_product.oe_number,
        brand=db_shop_product.brand,
        manufacturer=db_shop_product.manufacturer,
        model=db_shop_product.model,
        manufacturer_year=db_shop_product.manufacturer_year,
        compatible_vehicles=db_shop_product.compatible_vehicles,
        weight=db_shop_product.weight,
        dimensions=db_shop_product.dimensions,
        image=db_shop_product.image,
        is_featured=db_shop_product.is_featured,
        is_on_sale=db_shop_product.is_on_sale,
        stock_quantity=db_shop_product.stock_quantity,
        is_active=db_shop_product.is_active,
        created_at=db_shop_product.created_at,
        updated_at=db_shop_product.updated_at,
        categories=[{
            "id": str(cat.id), 
            "name": cat.name, 
            "slug": cat.slug, 
            "description": cat.description, 
            "parent_id": str(cat.parent_id) if cat.parent_id else None, 
            "image": cat.image, 
            "is_active": cat.is_active, 
            "created_at": cat.created_at.isoformat() if cat.created_at else None
        } for cat in db_shop_product.categories],
        shop_name=shop.name
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
    
    shop = updated_shop_product.shop
    
    # Prepare full response
    response = ShopProductFullResponse(
        id=updated_shop_product.id,
        shop_id=updated_shop_product.shop_id,
        name=updated_shop_product.name,
        slug=updated_shop_product.slug,
        description=updated_shop_product.description,
        technical_details=updated_shop_product.technical_details,
        price=updated_shop_product.price,
        sale_price=updated_shop_product.sale_price,
        sku=updated_shop_product.sku,
        oe_number=updated_shop_product.oe_number,
        brand=updated_shop_product.brand,
        manufacturer=updated_shop_product.manufacturer,
        model=updated_shop_product.model,
        manufacturer_year=updated_shop_product.manufacturer_year,
        compatible_vehicles=updated_shop_product.compatible_vehicles,
        weight=updated_shop_product.weight,
        dimensions=updated_shop_product.dimensions,
        image=updated_shop_product.image,
        is_featured=updated_shop_product.is_featured,
        is_on_sale=updated_shop_product.is_on_sale,
        stock_quantity=updated_shop_product.stock_quantity,
        is_active=updated_shop_product.is_active,
        created_at=updated_shop_product.created_at,
        updated_at=updated_shop_product.updated_at,
        categories=[{
            "id": str(cat.id), 
            "name": cat.name, 
            "slug": cat.slug, 
            "description": cat.description, 
            "parent_id": str(cat.parent_id) if cat.parent_id else None, 
            "image": cat.image, 
            "is_active": cat.is_active, 
            "created_at": cat.created_at.isoformat() if cat.created_at else None
        } for cat in updated_shop_product.categories],
        shop_name=shop.name
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
    
    # Prepare response with shop product information
    response = ShopProductResponse(
        id=updated_shop_product.id,
        shop_id=updated_shop_product.shop_id,
        name=updated_shop_product.name,
        slug=updated_shop_product.slug,
        description=updated_shop_product.description,
        technical_details=updated_shop_product.technical_details,
        price=updated_shop_product.price,
        sale_price=updated_shop_product.sale_price,
        sku=updated_shop_product.sku,
        oe_number=updated_shop_product.oe_number,
        brand=updated_shop_product.brand,
        manufacturer=updated_shop_product.manufacturer,
        model=updated_shop_product.model,
        manufacturer_year=updated_shop_product.manufacturer_year,
        compatible_vehicles=updated_shop_product.compatible_vehicles,
        weight=updated_shop_product.weight,
        dimensions=updated_shop_product.dimensions,
        image=updated_shop_product.image,
        is_featured=updated_shop_product.is_featured,
        is_on_sale=updated_shop_product.is_on_sale,
        stock_quantity=updated_shop_product.stock_quantity,
        is_active=updated_shop_product.is_active,
        created_at=updated_shop_product.created_at,
        updated_at=updated_shop_product.updated_at,
        categories=[{
            "id": str(cat.id), 
            "name": cat.name, 
            "slug": cat.slug, 
            "description": cat.description, 
            "parent_id": str(cat.parent_id) if cat.parent_id else None, 
            "image": cat.image, 
            "is_active": cat.is_active, 
            "created_at": cat.created_at.isoformat() if cat.created_at else None
        } for cat in updated_shop_product.categories]
    )
    
    return response


@router.get("/search", response_model=List[dict])
def search_products_endpoint(
    name: Optional[str] = None,
    oe_number: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Search for products by name or OE number across all shops
    """
    if not name and not oe_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either name or oe_number must be provided"
        )
    
    # Get shop products matching the criteria
    shop_info = get_shop_products_by_name_or_oe(db, name=name, oe_number=oe_number)
    
    return shop_info