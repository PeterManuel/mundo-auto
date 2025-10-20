from typing import List, Optional
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud.activity_log import (
    get_activity_log,
    get_activity_logs,
    get_user_activity_logs,
    get_recent_logs,
    delete_activity_log
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.activity_log import ActivityLogResponse, ActivityLogFilter


router = APIRouter()


@router.get("/", response_model=List[ActivityLogResponse])
def read_activity_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[uuid.UUID] = None,
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    path: Optional[str] = None,
    status_code: Optional[str] = None,
    ip_address: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all activity logs with filtering options. Only accessible by superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access logs"
        )
    
    # Create filter object from parameters
    filter_params = ActivityLogFilter(
        user_id=user_id,
        endpoint=endpoint,
        method=method,
        path=path,
        status_code=status_code,
        ip_address=ip_address,
        start_date=start_date,
        end_date=end_date
    )
    
    logs = get_activity_logs(db, skip=skip, limit=limit, filter_params=filter_params)
    return logs


@router.get("/recent", response_model=List[ActivityLogResponse])
def read_recent_logs(
    hours: int = Query(24, ge=1, le=168),  # Between 1 hour and 7 days
    limit: int = Query(100, ge=10, le=500),  # Between 10 and 500 results
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get recent activity logs. Only accessible by superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access logs"
        )
    
    logs = get_recent_logs(db, hours=hours, limit=limit)
    return logs


@router.get("/users/{user_id}", response_model=List[ActivityLogResponse])
def read_user_logs(
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get activity logs for a specific user. Accessible by superusers or the user themselves.
    """
    # Check permissions
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access these logs"
        )
    
    logs = get_user_activity_logs(db, user_id=user_id, skip=skip, limit=limit)
    return logs


@router.get("/{log_id}", response_model=ActivityLogResponse)
def read_activity_log(
    log_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific activity log by ID. Only accessible by superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access logs"
        )
    
    log = get_activity_log(db, log_id=log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found"
        )
    
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_log(
    log_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a specific activity log. Only accessible by superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to delete logs"
        )
    
    success = delete_activity_log(db, log_id=log_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found"
        )
    
    return None