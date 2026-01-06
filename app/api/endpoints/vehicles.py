from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud.vehicle import (
    get_vehicle,
    get_vehicles,
    create_vehicle,
    update_vehicle,
    delete_vehicle,
    get_all_vehicle_brands,
    get_all_vehicle_models,
    get_vehicle_shop_products,
    get_vehicles_with_shop_products
)
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse,
    VehicleWithProducts
)

router = APIRouter()


@router.get("/brands", response_model=List[str], status_code=status.HTTP_200_OK)
async def get_vehicle_brands(
    db: Session = Depends(get_db)
) -> List[str]:
    """
    Get all unique brands from active vehicles
    """
    return get_all_vehicle_brands(db)


@router.get("/models", response_model=List[str], status_code=status.HTTP_200_OK)
async def get_vehicle_models(
    brand: Optional[str] = Query(None, description="Filter models by brand name"),
    db: Session = Depends(get_db)
) -> List[str]:
    """
    Get all unique models from active vehicles.
    Optionally filter by brand name.
    """
    return get_all_vehicle_models(db, brand)


@router.get("/", response_model=List[dict])
def read_vehicles(
    brand: Optional[str] = None,
    model_names: Optional[str] = Query(None, description="Comma-separated model names"),
    manufacturer_year: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get vehicles with various filters
    
    - **brand**: Filter by brand name (partial match)
    - **model_names**: Filter by model names (comma-separated)
    - **manufacturer_year**: Filter by manufacturer year
    - **search**: Search in brand, model, description
    - **is_active**: Filter by active status
    """
    # Parse model_names if provided
    parsed_model_names = None
    if model_names:
        parsed_model_names = [name.strip() for name in model_names.split(',')]
    
    vehicles = get_vehicles(
        db,
        brand=brand,
        model_names=parsed_model_names,
        manufacturer_year=manufacturer_year,
        search_query=search,
        skip=skip,
        limit=limit,
        is_active=is_active
    )
    
    return vehicles


@router.get("/with-products", response_model=List[dict])
def read_vehicles_with_products(
    brand: Optional[str] = None,
    model_names: Optional[str] = Query(None, description="Comma-separated model names"),
    manufacturer_year: Optional[int] = None,
    category_id: Optional[uuid.UUID] = Query(None, description="Filter shop products by category ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get vehicles with their associated shop products
    
    - **brand**: Filter by brand name (partial match)
    - **model_names**: Filter by model names (comma-separated)
    - **manufacturer_year**: Filter by manufacturer year
    - **category_id**: Filter shop products by category ID
    """
    # Parse model_names if provided
    parsed_model_names = None
    if model_names:
        parsed_model_names = [name.strip() for name in model_names.split(',')]
    
    return get_vehicles_with_shop_products(
        db=db,
        brand=brand,
        model_names=parsed_model_names,
        manufacturer_year=manufacturer_year,
        category_id=category_id,
        skip=skip,
        limit=limit
    )


@router.get("/{vehicle_id}", response_model=dict)
def read_vehicle(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific vehicle
    """
    vehicle = get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    return vehicle


@router.get("/{vehicle_id}/shop-products", response_model=List[dict])
def read_vehicle_shop_products(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get all shop products associated with a vehicle
    """
    shop_products = get_vehicle_shop_products(db, vehicle_id)
    
    result = []
    for sp in shop_products:
        if sp.is_active:
            # Get primary image
            primary_image = None
            for image in sp.images:
                if image.is_primary:
                    primary_image = image.image_data
                    break
            if not primary_image and sp.images:
                primary_image = sp.images[0].image_data
            
            result.append({
                "id": str(sp.id),
                "name": sp.name,
                "slug": sp.slug,
                "description": sp.description,
                "price": sp.price,
                "sale_price": sp.sale_price,
                "brand": sp.brand,
                "sku": sp.sku,
                "oe_number": sp.oe_number,
                "shop_id": str(sp.shop_id),
                "shop_name": sp.shop.name if sp.shop else None,
                "stock_quantity": sp.stock_quantity,
                "is_featured": sp.is_featured,
                "is_on_sale": sp.is_on_sale,
                "primary_image": primary_image,
                "categories": [{
                    "id": str(cat.id),
                    "name": cat.name,
                    "slug": cat.slug
                } for cat in sp.categories],
                "created_at": sp.created_at,
                "updated_at": sp.updated_at
            })
    
    return result


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_vehicle_endpoint(
    vehicle: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new vehicle (Only superadmin can create vehicles)
    """
    # Check if user is superadmin
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can create vehicles"
        )
    
    # Create vehicle
    db_vehicle = create_vehicle(db, vehicle)
    return db_vehicle


@router.put("/{vehicle_id}", response_model=dict)
def update_vehicle_endpoint(
    vehicle_id: uuid.UUID,
    vehicle_update: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a vehicle (Only superadmin can update vehicles)
    """
    # Check if user is superadmin
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can update vehicles"
        )
    
    # Update vehicle
    updated_vehicle = update_vehicle(db, vehicle_id, vehicle_update)
    if not updated_vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    return updated_vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle_endpoint(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a vehicle (Only superadmin can delete vehicles)
    """
    # Check if user is superadmin
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can delete vehicles"
        )
    
    # Delete vehicle
    success = delete_vehicle(db, vehicle_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    return