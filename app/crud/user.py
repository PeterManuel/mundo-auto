from datetime import datetime
from typing import List, Optional, Union, Dict, Any
import uuid

from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User, LoginHistory, UserRole
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: uuid.UUID) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    
    if user:
        # Ensure no null values for required fields
        if user.is_active is None:
            user.is_active = True
        if user.is_superuser is None:
            user.is_superuser = False
        if user.created_at is None:
            user.created_at = datetime.utcnow()
    
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Ensure no null values for required fields
        if user.is_active is None:
            user.is_active = True
        if user.is_superuser is None:
            user.is_superuser = False
        if user.created_at is None:
            user.created_at = datetime.utcnow()
    
    return user


def get_users(
    db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
) -> List[User]:
    query = db.query(User)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    users = query.offset(skip).limit(limit).all()
    
    # Ensure no null values for required fields
    for user in users:
        if user.is_active is None:
            user.is_active = True
        if user.is_superuser is None:
            user.is_superuser = False
        if user.created_at is None:
            user.created_at = datetime.utcnow()
    
    return users


def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    user_data = {
        "email": user.email,
        "hashed_password": hashed_password,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number,
        "address": user.address,
        "profile_image": user.profile_image,
        "role": user.role,
        "shop_id": user.shop_id,
    }
    
    # If AdminUserCreate was used, include additional fields
    if hasattr(user, "is_superuser"):
        user_data["is_superuser"] = user.is_superuser
    if hasattr(user, "is_active"):
        user_data["is_active"] = user.is_active
    
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: uuid.UUID, user: UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: uuid.UUID) -> bool:
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    # Ensure no null values for required fields
    if user.is_active is None:
        user.is_active = True
    if user.is_superuser is None:
        user.is_superuser = False
    if user.created_at is None:
        user.created_at = datetime.utcnow()
    
    return user


def record_login_history(
    db: Session, user_id: uuid.UUID, ip_address: Optional[str] = None, user_agent: Optional[str] = None
) -> LoginHistory:
    login_record = LoginHistory(
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(login_record)
    db.commit()
    db.refresh(login_record)
    return login_record


def get_login_history(
    db: Session, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> List[LoginHistory]:
    return (
        db.query(LoginHistory)
        .filter(LoginHistory.user_id == user_id)
        .order_by(LoginHistory.login_timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_user_role(db: Session, user_id: uuid.UUID, role: UserRole) -> Optional[User]:
    """
    Update a user's role. This is an admin-only function.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.role = role
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def activate_deactivate_user(db: Session, user_id: uuid.UUID, is_active: bool) -> Optional[User]:
    """
    Activate or deactivate a user account. This is an admin-only function.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.is_active = is_active
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def search_users(
    db: Session,
    search_term: Optional[str] = None,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    shop_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "created_at",
    sort_desc: bool = True
) -> List[User]:
    """
    Search and filter users by various criteria.
    """
    query = db.query(User)
    
    # Apply filters
    if search_term:
        # Search in email, first_name, last_name, phone_number
        search = f"%{search_term}%"
        query = query.filter(
            or_(
                User.email.ilike(search),
                User.first_name.ilike(search),
                User.last_name.ilike(search),
                User.phone_number.ilike(search)
            )
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if shop_id:
        query = query.filter(User.shop_id == shop_id)
    
    # Apply sorting
    if sort_by:
        column = getattr(User, sort_by, None)
        if column is not None:
            query = query.order_by(desc(column) if sort_desc else column)
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    # Ensure no null values for required fields
    for user in users:
        if user.is_active is None:
            user.is_active = True
        if user.is_superuser is None:
            user.is_superuser = False
        if user.created_at is None:
            user.created_at = datetime.utcnow()
    
    return users


def count_users(
    db: Session,
    search_term: Optional[str] = None,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    shop_id: Optional[uuid.UUID] = None
) -> int:
    """
    Count users matching filter criteria.
    """
    query = db.query(func.count(User.id))
    
    # Apply filters
    if search_term:
        # Search in email, first_name, last_name, phone_number
        search = f"%{search_term}%"
        query = query.filter(
            or_(
                User.email.ilike(search),
                User.first_name.ilike(search),
                User.last_name.ilike(search),
                User.phone_number.ilike(search)
            )
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    if shop_id:
        query = query.filter(User.shop_id == shop_id)
    
    return query.scalar()


def bulk_activate_deactivate_users(
    db: Session, user_ids: List[uuid.UUID], is_active: bool
) -> Dict[uuid.UUID, bool]:
    """
    Bulk activate or deactivate multiple user accounts at once.
    Returns a dictionary of user_id: success pairs.
    """
    results = {}
    for user_id in user_ids:
        db_user = get_user(db, user_id)
        if not db_user:
            results[user_id] = False
            continue
        
        db_user.is_active = is_active
        results[user_id] = True
    
    db.commit()
    return results