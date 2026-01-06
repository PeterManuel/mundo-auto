from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.models.vehicle_brand import VehicleBrand
from app.schemas.vehicle import VehicleBrandCreate, VehicleBrandUpdate


def get_vehicle_brand(db: Session, brand_id: uuid.UUID) -> Optional[VehicleBrand]:
    """Get vehicle brand by ID"""
    return db.query(VehicleBrand).filter(VehicleBrand.id == brand_id).first()


def get_vehicle_brand_by_name(db: Session, name: str) -> Optional[VehicleBrand]:
    """Get vehicle brand by name"""
    return db.query(VehicleBrand).filter(VehicleBrand.name.ilike(name)).first()


def get_vehicle_brands(
    db: Session,
    search_query: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[VehicleBrand]:
    """
    Get vehicle brands with filters
    """
    query = db.query(VehicleBrand)
    
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            VehicleBrand.name.ilike(search_term) | 
            VehicleBrand.description.ilike(search_term)
        )
    
    if is_active is not None:
        query = query.filter(VehicleBrand.is_active == is_active)
    
    return query.order_by(VehicleBrand.name).offset(skip).limit(limit).all()


def create_vehicle_brand(db: Session, brand: VehicleBrandCreate) -> VehicleBrand:
    """Create a new vehicle brand"""
    db_brand = VehicleBrand(**brand.dict())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand


def update_vehicle_brand(
    db: Session, brand_id: uuid.UUID, brand: VehicleBrandUpdate
) -> Optional[VehicleBrand]:
    """Update a vehicle brand"""
    db_brand = get_vehicle_brand(db, brand_id)
    if not db_brand:
        return None
    
    update_data = brand.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_brand, field, value)
    
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand


def delete_vehicle_brand(db: Session, brand_id: uuid.UUID) -> bool:
    """Delete a vehicle brand"""
    db_brand = get_vehicle_brand(db, brand_id)
    if not db_brand:
        return False
    
    db.delete(db_brand)
    db.commit()
    return True


def get_all_vehicle_brand_names(db: Session) -> List[str]:
    """Get all unique vehicle brand names from active brands"""
    query = (
        db.query(VehicleBrand.name)
        .filter(VehicleBrand.is_active == True)
        .order_by(VehicleBrand.name)
    )
    return [brand[0] for brand in query.all()]