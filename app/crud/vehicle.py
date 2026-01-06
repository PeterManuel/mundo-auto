from typing import List, Optional, Dict
import uuid

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.vehicle import Vehicle
from app.models.vehicle_model import VehicleModel
from app.models.shop_product import ShopProduct
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


def get_vehicle(db: Session, vehicle_id: uuid.UUID) -> Optional[Dict]:
    """Get vehicle by ID"""
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        return None
    
    # Serialize vehicle with models as dictionaries
    models_list = [{
        "id": str(model.id),
        "name": model.name,
        "description": model.description,
        "is_active": model.is_active,
        "created_at": model.created_at,
        "updated_at": model.updated_at
    } for model in vehicle.models]
    
    return {
        "id": str(vehicle.id),
        "brand": vehicle.brand,
        "manufacturer_year": vehicle.manufacturer_year,
        "description": vehicle.description,
        "is_active": vehicle.is_active,
        "created_at": vehicle.created_at,
        "updated_at": vehicle.updated_at,
        "models": models_list
    }


def get_vehicle_by_brand_models_year(
    db: Session, brand: str, model_ids: List[uuid.UUID], manufacturer_year: Optional[int] = None
) -> Optional[Vehicle]:
    """Get vehicle by brand string, model IDs, and optional year"""
    query = db.query(Vehicle).join(Vehicle.models).filter(
        Vehicle.brand == brand,
        VehicleModel.id.in_(model_ids)
    )
    
    if manufacturer_year:
        query = query.filter(Vehicle.manufacturer_year == manufacturer_year)
    
    return query.first()


def get_vehicles(
    db: Session,
    brand: Optional[str] = None,
    model_names: Optional[List[str]] = None,
    manufacturer_year: Optional[int] = None,
    search_query: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[Dict]:
    """
    Get vehicles with various filters
    
    Args:
        db: Database session
        brand: Filter by brand name (string)
        model_names: Filter by model names
        manufacturer_year: Filter by manufacturer year
        search_query: Search in brand name, model name, description
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status
    """
    query = (
        db.query(Vehicle)
        .outerjoin(Vehicle.models)
    )
    
    # Apply filters
    if brand:
        query = query.filter(Vehicle.brand.ilike(f"%{brand}%"))
    
    if model_names:
        query = query.filter(VehicleModel.name.in_(model_names))
    
    if manufacturer_year:
        query = query.filter(Vehicle.manufacturer_year == manufacturer_year)
    
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            (Vehicle.brand.ilike(search_term)) | 
            (VehicleModel.name.ilike(search_term)) | 
            (Vehicle.description.ilike(search_term))
        )
    
    if is_active is not None:
        query = query.filter(Vehicle.is_active == is_active)
    
    vehicles = query.distinct().offset(skip).limit(limit).all()
    
    # Serialize vehicles with models as dictionaries
    result = []
    for vehicle in vehicles:
        models_list = [{
            "id": str(model.id),
            "name": model.name,
            "description": model.description,
            "is_active": model.is_active,
            "created_at": model.created_at,
            "updated_at": model.updated_at
        } for model in vehicle.models]
        
        result.append({
            "id": str(vehicle.id),
            "brand": vehicle.brand,
            "manufacturer_year": vehicle.manufacturer_year,
            "description": vehicle.description,
            "is_active": vehicle.is_active,
            "created_at": vehicle.created_at,
            "updated_at": vehicle.updated_at,
            "models": models_list
        })
    
    return result


def create_vehicle(db: Session, vehicle: VehicleCreate) -> Dict:
    """
    Create a new vehicle
    """
    db_vehicle = Vehicle(**vehicle.dict())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    
    # Serialize vehicle with models as dictionaries
    models_list = [{
        "id": str(model.id),
        "name": model.name,
        "description": model.description,
        "is_active": model.is_active,
        "created_at": model.created_at,
        "updated_at": model.updated_at
    } for model in db_vehicle.models]
    
    return {
        "id": str(db_vehicle.id),
        "brand": db_vehicle.brand,
        "manufacturer_year": db_vehicle.manufacturer_year,
        "description": db_vehicle.description,
        "is_active": db_vehicle.is_active,
        "created_at": db_vehicle.created_at,
        "updated_at": db_vehicle.updated_at,
        "models": models_list
    }


def update_vehicle(
    db: Session, vehicle_id: uuid.UUID, vehicle: VehicleUpdate
) -> Optional[Dict]:
    """
    Update a vehicle
    """
    db_vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not db_vehicle:
        return None
    
    update_data = vehicle.dict(exclude_unset=True)
    
    # Update vehicle fields
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)
    
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    
    # Serialize vehicle with models as dictionaries
    models_list = [{
        "id": str(model.id),
        "name": model.name,
        "description": model.description,
        "is_active": model.is_active,
        "created_at": model.created_at,
        "updated_at": model.updated_at
    } for model in db_vehicle.models]
    
    return {
        "id": str(db_vehicle.id),
        "brand": db_vehicle.brand,
        "manufacturer_year": db_vehicle.manufacturer_year,
        "description": db_vehicle.description,
        "is_active": db_vehicle.is_active,
        "created_at": db_vehicle.created_at,
        "updated_at": db_vehicle.updated_at,
        "models": models_list
    }


def delete_vehicle(db: Session, vehicle_id: uuid.UUID) -> bool:
    """
    Delete a vehicle
    """
    db_vehicle = get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return False
    
    db.delete(db_vehicle)
    db.commit()
    return True


def get_all_vehicle_brands(db: Session) -> List[str]:
    """
    Get all unique vehicle brands from active vehicles
    """
    query = (
        db.query(Vehicle.brand)
        .filter(
            Vehicle.is_active == True,
            Vehicle.brand.isnot(None)
        )
        .distinct()
        .order_by(Vehicle.brand)
    )
    return [brand[0] for brand in query.all() if brand[0]]


def get_all_vehicle_models(db: Session, brand: Optional[str] = None) -> List[str]:
    """
    Get all unique vehicle models from active vehicles
    
    Args:
        db: Database session
        brand: Optional brand name to filter models by
    """
    query = (
        db.query(VehicleModel.name)
        .join(Vehicle.models)
        .filter(
            Vehicle.is_active == True,
            VehicleModel.is_active == True
        )
    )
    
    if brand:
        query = query.filter(Vehicle.brand.ilike(f"%{brand}%"))
    
    query = query.distinct().order_by(VehicleModel.name)
    return [model[0] for model in query.all()]


def get_vehicle_shop_products(db: Session, vehicle_id: uuid.UUID) -> List[ShopProduct]:
    """
    Get all shop products associated with a vehicle
    """
    vehicle = get_vehicle(db, vehicle_id)
    if not vehicle:
        return []
    
    return vehicle.shop_products


def get_vehicles_with_shop_products(
    db: Session,
    brand: Optional[str] = None,
    model_names: Optional[List[str]] = None,
    manufacturer_year: Optional[int] = None,
    category_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Dict]:
    """
    Get vehicles with their associated shop products count and details
    
    Args:
        db: Database session
        brand: Filter vehicles by brand name
        model_names: Filter vehicles by model names
        manufacturer_year: Filter vehicles by manufacturer year
        category_id: Filter shop products by category ID
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Note: AND logic is applied - only vehicles matching ALL provided filters
    and having at least one matching shop product are returned when filters are given.
    """
    # Track if any filter is provided to determine AND logic behavior
    has_filters = any([brand, model_names, category_id])
    
    # Query Vehicle ORM objects directly (not serialized dicts) to access relationships
    query = (
        db.query(Vehicle)
        .outerjoin(Vehicle.models)
        .filter(Vehicle.is_active == True)
    )
    
    if brand:
        query = query.filter(Vehicle.brand.ilike(f"%{brand}%"))
    
    if model_names:
        query = query.filter(VehicleModel.name.in_(model_names))
    
    if manufacturer_year:
        query = query.filter(Vehicle.manufacturer_year == manufacturer_year)
    
    vehicles = query.distinct().offset(skip).limit(limit).all()
    
    result = []
    for vehicle in vehicles:
        shop_products = []
        for sp in vehicle.shop_products:
            if sp.is_active:
                # Filter by category if provided
                if category_id:
                    # Check if any of the shop product's categories match the category_id
                    category_matches = any(
                        cat.id == category_id
                        for cat in sp.categories
                    )
                    if not category_matches:
                        continue
                
                # Get primary image
                primary_image = None
                images_list = []
                for image in sp.images:
                    image_data = {
                        "id": str(image.id),
                        "image_data": image.image_data,
                        "alt_text": image.alt_text,
                        "is_primary": image.is_primary,
                        "display_order": image.display_order,
                        "created_at": image.created_at
                    }
                    images_list.append(image_data)
                    if image.is_primary:
                        primary_image = image.image_data
                if not primary_image and sp.images:
                    primary_image = sp.images[0].image_data
                
                shop_products.append({
                    "id": str(sp.id),
                    "name": sp.name,
                    "slug": sp.slug,
                    "description": sp.description,
                    "technical_details": sp.technical_details,
                    "price": sp.price,
                    "sale_price": sp.sale_price,
                    "brand": sp.brand,
                    "manufacturer": sp.manufacturer,
                    "model": sp.model,
                    "manufacturer_year": sp.manufacturer_year,
                    "compatible_vehicles": sp.compatible_vehicles,
                    "sku": sp.sku,
                    "oe_number": sp.oe_number,
                    "weight": sp.weight,
                    "dimensions": sp.dimensions,
                    "shop_id": str(sp.shop_id),
                    "shop_name": sp.shop.name if sp.shop else None,
                    "stock_quantity": sp.stock_quantity,
                    "is_featured": sp.is_featured,
                    "is_on_sale": sp.is_on_sale,
                    "is_active": sp.is_active,
                    "primary_image": primary_image,
                    "images": images_list,
                    "categories": [{
                        "id": str(cat.id),
                        "name": cat.name,
                        "slug": cat.slug
                    } for cat in sp.categories],
                    "created_at": sp.created_at,
                    "updated_at": sp.updated_at
                })
        
        # Prepare models list
        models_list = [{
            "id": str(model.id),
            "name": model.name,
            "description": model.description
        } for model in vehicle.models]
        
        # Only include vehicles that have at least one matching shop product
        # when filters are provided (AND logic). If no filters, include all vehicles with products.
        if has_filters:
            # Strict AND logic: must have matching products when filters are given
            if shop_products:
                result.append({
                    "id": str(vehicle.id),
                    "brand": vehicle.brand,
                    "models": models_list,
                    "manufacturer_year": vehicle.manufacturer_year,
                    "description": vehicle.description,
                    "is_active": vehicle.is_active,
                    "created_at": vehicle.created_at,
                    "updated_at": vehicle.updated_at,
                    "shop_products": shop_products,
                    "shop_products_count": len(shop_products)
                })
        else:
            # No filters: return all vehicles with their products
            result.append({
                "id": str(vehicle.id),
                "brand": vehicle.brand,
                "models": models_list,
                "manufacturer_year": vehicle.manufacturer_year,
                "description": vehicle.description,
                "is_active": vehicle.is_active,
                "created_at": vehicle.created_at,
                "updated_at": vehicle.updated_at,
                "shop_products": shop_products,
                "shop_products_count": len(shop_products)
            })
    
    return result