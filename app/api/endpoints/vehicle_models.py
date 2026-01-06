from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud.vehicle_model import (
    get_vehicle_model,
    get_vehicle_models,
    create_vehicle_model,
    update_vehicle_model,
    delete_vehicle_model,
    get_all_vehicle_model_names,
    get_vehicle_model_by_name
)
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.vehicle import (
    VehicleModelCreate,
    VehicleModelUpdate,
    VehicleModelResponse
)

router = APIRouter()


@router.get("/", response_model=List[VehicleModelResponse])
def read_vehicle_models(
    search: Optional[str] = Query(None, description="Search models by name or description"),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Get vehicle models with various filters
    
    - **search**: Search in model name and description
    - **is_active**: Filter by active status
    """
    vehicle_models = get_vehicle_models(
        db,
        search_query=search,
        skip=skip,
        limit=limit,
        is_active=is_active
    )
    
    return vehicle_models


@router.get("/names", response_model=List[str], status_code=status.HTTP_200_OK)
async def get_vehicle_model_names(
    db: Session = Depends(get_db)
) -> List[str]:
    """
    Get all unique model names from active models
    """
    return get_all_vehicle_model_names(db)


@router.get("/{model_id}", response_model=VehicleModelResponse)
def read_vehicle_model(
    model_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific vehicle model
    """
    vehicle_model = get_vehicle_model(db, model_id)
    if not vehicle_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle model not found"
        )
    
    return vehicle_model


@router.post("/", response_model=VehicleModelResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle_model_endpoint(
    vehicle_model: VehicleModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new vehicle model (Only superadmin can create models)
    """
    # Check if user is superadmin
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can create vehicle models"
        )
    
    # Check if model with same name already exists
    existing_model = get_vehicle_model_by_name(db, vehicle_model.name)
    if existing_model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vehicle model with name '{vehicle_model.name}' already exists"
        )
    
    # Create vehicle model
    db_vehicle_model = create_vehicle_model(db, vehicle_model)
    return db_vehicle_model


@router.put("/{model_id}", response_model=VehicleModelResponse)
def update_vehicle_model_endpoint(
    model_id: uuid.UUID,
    vehicle_model_update: VehicleModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a vehicle model (Only superadmin can update models)
    """
    # Check if user is superadmin
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can update vehicle models"
        )
    
    # Check if name is being changed and if new name already exists
    if vehicle_model_update.name:
        existing_model = get_vehicle_model_by_name(db, vehicle_model_update.name)
        if existing_model and existing_model.id != model_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vehicle model with name '{vehicle_model_update.name}' already exists"
            )
    
    # Update vehicle model
    updated_vehicle_model = update_vehicle_model(db, model_id, vehicle_model_update)
    if not updated_vehicle_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle model not found"
        )
    
    return updated_vehicle_model


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle_model_endpoint(
    model_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a vehicle model (Only superadmin can delete models)
    """
    # Check if user is superadmin
    if current_user.role != UserRole.SUPERADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can delete vehicle models"
        )
    
    # Delete vehicle model
    success = delete_vehicle_model(db, model_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle model not found"
        )
    
    return