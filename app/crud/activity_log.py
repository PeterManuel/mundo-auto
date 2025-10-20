import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import uuid

from fastapi import HTTPException, status
from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.schemas.activity_log import ActivityLogCreate, ActivityLogUpdate, ActivityLogFilter


def create_activity_log(db: Session, log_data: Union[ActivityLogCreate, Dict[str, Any]]) -> ActivityLog:
    """
    Create a new activity log entry
    """
    if isinstance(log_data, dict):
        db_log = ActivityLog(**log_data)
    else:
        db_log = ActivityLog(
            user_id=log_data.user_id,
            endpoint=log_data.endpoint,
            method=log_data.method,
            path=log_data.path,
            status_code=log_data.status_code,
            request_body=log_data.request_body,
            response_body=log_data.response_body,
            ip_address=log_data.ip_address,
            user_agent=log_data.user_agent,
            device_type=log_data.device_type,
            browser=log_data.browser,
            os=log_data.os,
            extra_data=log_data.extra_data,
            processing_time_ms=log_data.processing_time_ms
        )
    
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_activity_log(db: Session, log_id: uuid.UUID) -> Optional[ActivityLog]:
    """
    Get a specific activity log by ID
    """
    return db.query(ActivityLog).filter(ActivityLog.id == log_id).first()


def get_activity_logs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    filter_params: Optional[ActivityLogFilter] = None
) -> List[ActivityLog]:
    """
    Get activity logs with optional filtering
    """
    query = db.query(ActivityLog)
    
    if filter_params:
        if filter_params.user_id:
            query = query.filter(ActivityLog.user_id == filter_params.user_id)
            
        if filter_params.endpoint:
            query = query.filter(ActivityLog.endpoint.ilike(f"%{filter_params.endpoint}%"))
            
        if filter_params.method:
            query = query.filter(ActivityLog.method == filter_params.method)
            
        if filter_params.path:
            query = query.filter(ActivityLog.path.ilike(f"%{filter_params.path}%"))
            
        if filter_params.status_code:
            query = query.filter(ActivityLog.status_code == filter_params.status_code)
            
        if filter_params.ip_address:
            query = query.filter(ActivityLog.ip_address == filter_params.ip_address)
            
        if filter_params.start_date and filter_params.end_date:
            query = query.filter(
                and_(
                    ActivityLog.created_at >= filter_params.start_date,
                    ActivityLog.created_at <= filter_params.end_date
                )
            )
        elif filter_params.start_date:
            query = query.filter(ActivityLog.created_at >= filter_params.start_date)
        elif filter_params.end_date:
            query = query.filter(ActivityLog.created_at <= filter_params.end_date)
            
    # Always sort by most recent first
    query = query.order_by(desc(ActivityLog.created_at))
    
    return query.offset(skip).limit(limit).all()


def get_user_activity_logs(
    db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> List[ActivityLog]:
    """
    Get activity logs for a specific user
    """
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(desc(ActivityLog.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_recent_logs(db: Session, hours: int = 24, limit: int = 100) -> List[ActivityLog]:
    """
    Get recent activity logs within the specified time period
    """
    start_time = datetime.utcnow() - timedelta(hours=hours)
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.created_at >= start_time)
        .order_by(desc(ActivityLog.created_at))
        .limit(limit)
        .all()
    )


def delete_activity_log(db: Session, log_id: uuid.UUID) -> bool:
    """
    Delete an activity log entry
    """
    db_log = get_activity_log(db, log_id)
    if not db_log:
        return False
    
    db.delete(db_log)
    db.commit()
    return True