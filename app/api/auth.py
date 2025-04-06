# app/api/auth.py
from datetime import timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.crud.user import (
    get_user_by_email, 
    create_user, 
    get_user_by_id,
    get_users,
    update_user,
    delete_user
)
from app.crud.token import (
    create_refresh_token,
    get_refresh_token,
    invalidate_refresh_token
)
from app.crud.role import (
    get_all_roles,
    get_role_by_id,
    create_role,
    update_role,
    delete_role,
    assign_role_to_user
)
from app.core.security import (
    verify_password, 
    create_access_token
)
from app.api.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_admin_user
)
from app.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    TokenResponse,
    RefreshTokenRequest,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    UserRoleAssign
)

router = APIRouter()

# Core Authentication APIs

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token.token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    if get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = create_user(db, user_data)
    return user

@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    token_entry = get_refresh_token(db, refresh_data.refresh_token)
    
    if not token_entry or token_entry.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from refresh token
    user = get_user_by_id(db, token_entry.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create new access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": token_entry.token,  # Return same refresh token
        "token_type": "bearer"
    }

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Invalidate the refresh token
    invalidate_refresh_token(db, refresh_data.refresh_token)
    return None

# User Management APIs

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_email(db, current_user["email"])
    return user

@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Only allow admins or the user themselves to access a user profile
    if current_user.get("role") != "admin" and current_user.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/users", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    users = get_users(db, skip=skip, limit=limit)
    return users

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user_profile(
    user_id: str,
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Only allow admins or the user themselves to update a profile
    if current_user.get("role") != "admin" and current_user.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # If the user is not an admin, remove any attempt to change the role
    if current_user.get("role") != "admin":
        user_data.role = None
    
    updated_user = update_user(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    user_id: str,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    user = delete_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None

# Authorization & Roles APIs

@router.get("/roles", response_model=List[RoleResponse])
async def read_roles(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    roles = get_all_roles(db)
    return roles

@router.get("/roles/{role_id}", response_model=RoleResponse)
async def read_role(
    role_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    role = get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_new_role(
    role_data: RoleCreate,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    role = create_role(db, role_data)
    return role

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role_permissions(
    role_id: str,
    role_data: RoleUpdate,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    updated_role = update_role(db, role_id, role_data)
    if not updated_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return updated_role

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_role(
    role_id: str,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    deleted = delete_role(db, role_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return None

@router.post("/users/{user_id}/roles", response_model=UserResponse)
async def assign_roles(
    user_id: str,
    role_data: UserRoleAssign,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    updated_user = assign_role_to_user(db, user_id, role_data.role_id)
    return updated_user