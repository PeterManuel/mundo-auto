from typing import List, Optional, Dict
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
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
    get_user_by_email,
    update_user_role,
    activate_deactivate_user,
    search_users,
    count_users,
    bulk_activate_deactivate_users,
)
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    LoginHistoryResponse,
    AdminUserCreate,
    UserRoleUpdate,
    UserActivationUpdate,
    UserFilter,
    UserCount,
    BulkUserIds,
    BulkOperationResponse,
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


@router.post("/admin/create", response_model=UserResponse)
def admin_create_user(
    user: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new user with specified role. Only accessible by superusers.
    Superadmins can create other superadmins or logist users.
    """
    # Check if current user is a superuser
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only superadmins can create other admin users"
        )
    
    # Validate role - only allow creating LOGIST or ADMIN or SUPERADMIN roles
    if user.role not in [UserRole.LOGIST, UserRole.ADMIN, UserRole.SUPERADMIN]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role for admin creation. Must be one of: {UserRole.LOGIST}, {UserRole.ADMIN}, or {UserRole.SUPERADMIN}"
        )
    
    # Check if user with this email already exists
    existing_user = get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )
    
    # Ensure shop_id is provided for LOGIST users
    if user.role == UserRole.LOGIST and not user.shop_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Shop ID must be provided for users with LOGIST role"
        )
    
    # Create the user
    db_user = create_user(db, user)
    return db_user


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


@router.put("/{user_id}", response_model=UserResponse)
def admin_update_user(
    user_id: uuid.UUID,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a user. Admin only.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    # Check if the user exists
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Perform the update
    updated_user = update_user(db, user_id=user_id, user=user)
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a user. Admin only.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    # Check if the user exists
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Cannot delete yourself
    if str(user_id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user")
    
    return None


@router.put("/{user_id}/role", response_model=UserResponse)
def admin_update_user_role(
    user_id: uuid.UUID,
    role_update: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a user's role. Admin only.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    # Check if the user exists
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Cannot change your own role
    if str(user_id) == str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    # Perform the role update
    updated_user = update_user_role(db, user_id=user_id, role=role_update.role)
    return updated_user


@router.put("/{user_id}/activate", response_model=UserResponse)
def admin_activate_deactivate_user(
    user_id: uuid.UUID,
    activation: UserActivationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Activate or deactivate a user account. Admin only.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    # Check if the user exists
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Cannot deactivate your own account
    if str(user_id) == str(current_user.id) and not activation.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    # Perform the activation/deactivation
    updated_user = activate_deactivate_user(db, user_id=user_id, is_active=activation.is_active)
    return updated_user


@router.post("/search", response_model=List[UserResponse])
def search_filter_users(
    user_filter: UserFilter,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search and filter users. Admin only.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    users = search_users(
        db,
        search_term=user_filter.search_term,
        role=user_filter.role,
        is_active=user_filter.is_active,
        shop_id=user_filter.shop_id,
        skip=user_filter.skip,
        limit=user_filter.limit,
        sort_by=user_filter.sort_by,
        sort_desc=user_filter.sort_desc
    )
    
    return users


@router.post("/count", response_model=UserCount)
def count_filtered_users(
    user_filter: UserFilter,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Count users matching filter criteria. Admin only.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    count = count_users(
        db,
        search_term=user_filter.search_term,
        role=user_filter.role,
        is_active=user_filter.is_active,
        shop_id=user_filter.shop_id
    )
    
    return UserCount(count=count)


@router.post("/bulk/activate", response_model=BulkOperationResponse)
def bulk_activate_users(
    bulk_data: BulkUserIds,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk activate multiple users. Admin only.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    # Check if user is trying to activate/deactivate their own account
    if current_user.id in bulk_data.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own account in bulk operations"
        )
    
    results = bulk_activate_deactivate_users(db, bulk_data.user_ids, is_active=True)
    
    # Convert UUID keys to strings for the response
    str_results = {str(k): v for k, v in results.items()}
    success_count = sum(1 for v in results.values() if v)
    failure_count = sum(1 for v in results.values() if not v)
    
    return BulkOperationResponse(
        results=str_results,
        success_count=success_count,
        failure_count=failure_count
    )


@router.post("/bulk/deactivate", response_model=BulkOperationResponse)
def bulk_deactivate_users(
    bulk_data: BulkUserIds,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk deactivate multiple users. Admin only.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    # Check if user is trying to activate/deactivate their own account
    if current_user.id in bulk_data.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own account in bulk operations"
        )
    
    results = bulk_activate_deactivate_users(db, bulk_data.user_ids, is_active=False)
    
    # Convert UUID keys to strings for the response
    str_results = {str(k): v for k, v in results.items()}
    success_count = sum(1 for v in results.values() if v)
    failure_count = sum(1 for v in results.values() if not v)
    
    return BulkOperationResponse(
        results=str_results,
        success_count=success_count,
        failure_count=failure_count
    )