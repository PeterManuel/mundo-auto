from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.api.endpoints.auth import get_current_user
from app.crud.user import (
    get_user,
    get_users,
    create_user,
    update_user,
    delete_user,
    get_login_history,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginHistoryResponse,
)
from app.utils.file_upload import save_upload_file

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all users. Only accessible by superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_user)):
    """
    Get current user info
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_user_me(
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update current user info
    """
    db_user = update_user(db, user_id=current_user.id, user=user)
    return db_user


@router.post("/me/upload-avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload user avatar
    """
    # Save file
    filename = await save_upload_file(file, "avatars")
    file_url = f"/uploads/avatars/{filename}"
    
    # Update user profile
    user_update = UserUpdate(profile_image=file_url)
    db_user = update_user(db, user_id=current_user.id, user=user_update)
    
    return db_user


@router.get("/me/login-history", response_model=List[LoginHistoryResponse])
def read_login_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get login history for current user
    """
    login_history = get_login_history(db, user_id=current_user.id, skip=skip, limit=limit)
    return login_history


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get user by ID. Admin only or self.
    """
    if str(current_user.id) != str(user_id) and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    user = get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user