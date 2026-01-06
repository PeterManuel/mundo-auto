from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.models.vehicle_model import VehicleModel
from app.schemas.vehicle import VehicleModelCreate, VehicleModelUpdate


def get_vehicle_model(db: Session, model_id: uuid.UUID) -> Optional[VehicleModel]:
    """Get vehicle model by ID"""
    return db.query(VehicleModel).filter(VehicleModel.id == model_id).first()


def get_vehicle_model_by_name(db: Session, name: str) -> Optional[VehicleModel]:
    """Get vehicle model by name"""
    return db.query(VehicleModel).filter(
        VehicleModel.name.ilike(name)
    ).first()


def get_vehicle_models(
    db: Session,
    search_query: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[VehicleModel]:
    """
    Get vehicle models with filters
    """
    query = db.query(VehicleModel)
    
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            VehicleModel.name.ilike(search_term) | 
            VehicleModel.description.ilike(search_term)
        )
    
    if is_active is not None:
        query = query.filter(VehicleModel.is_active == is_active)
    
    return query.order_by(VehicleModel.name).offset(skip).limit(limit).all()


def create_vehicle_model(db: Session, model: VehicleModelCreate) -> VehicleModel:
    """Create a new vehicle model"""
    db_model = VehicleModel(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


def update_vehicle_model(
    db: Session, model_id: uuid.UUID, model: VehicleModelUpdate
) -> Optional[VehicleModel]:
    """Update a vehicle model"""
    db_model = get_vehicle_model(db, model_id)
    if not db_model:
        return None
    
    update_data = model.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_model, field, value)
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


def delete_vehicle_model(db: Session, model_id: uuid.UUID) -> bool:
    """Delete a vehicle model"""
    db_model = get_vehicle_model(db, model_id)
    if not db_model:
        return False
    
    db.delete(db_model)
    db.commit()
    return True


def get_all_vehicle_model_names(db: Session) -> List[str]:
    """Get all unique vehicle model names from active models"""
    query = db.query(VehicleModel.name).filter(VehicleModel.is_active == True)
    
    query = query.order_by(VehicleModel.name)
    return [model[0] for model in query.all()]