import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user, require_permission
from app.schemas.user import UserOut, UserCreate, UserUpdate
from app.repositories.user import UserRepository
from app.repositories.audit import AuditRepository
from app.models.users import User

router: APIRouter = APIRouter(prefix="/users", tags=["Users Management"])

@router.get("", response_model=List[UserOut])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("read:users"))
) -> List[User]:
    """
    List all system users. Requires 'read:users' permission.
    """
    user_repo = UserRepository(db)
    return await user_repo.list_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserOut)
async def read_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Gets details of a single user.
    Users can access their own profile; others require 'read:users' permission.
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    # Authorize: self or has permission
    user_permissions = [p.name for p in current_user.role.permissions]
    if current_user.id != user_id and "read:users" not in user_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions."
        )
    return user

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    schema: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("write:users"))
) -> User:
    """
    Register a new user inside the system. Requires 'write:users' permission.
    """
    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)
    
    existing = await user_repo.get_user_by_email(schema.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address already registered."
        )
        
    role = await user_repo.get_role_by_id(schema.role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role ID specified does not exist."
        )

    user = await user_repo.create_user(schema)

    # Log audit event
    await audit_repo.log_action(
        actor_id=current_user.id,
        action_type="user_create",
        description=f"Created user {user.email}",
        resource_id=str(user.id),
        metadata={"role": role.name}
    )
    return user

@router.put("/{user_id}", response_model=UserOut)
async def update_user_details(
    user_id: uuid.UUID,
    schema: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Updates user details.
    Users can update their own details; others require 'write:users' permission.
    """
    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)
    
    user = await user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    user_permissions = [p.name for p in current_user.role.permissions]
    if current_user.id != user_id and "write:users" not in user_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions."
        )

    if schema.role_id is not None and "write:users" not in user_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auditors/Users cannot assign or update roles."
        )

    updated_user = await user_repo.update_user(user, schema)

    # Log audit event
    await audit_repo.log_action(
        actor_id=current_user.id,
        action_type="user_update",
        description=f"Updated user details for {updated_user.email}",
        resource_id=str(updated_user.id)
    )
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_record(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("delete:users"))
) -> None:
    """
    Removes a user record. Requires 'delete:users' permission.
    """
    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)
    
    user = await user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    await user_repo.delete_user(user)

    # Log audit event
    await audit_repo.log_action(
        actor_id=current_user.id,
        action_type="user_delete",
        description=f"Deleted user {user.email}",
        resource_id=str(user_id)
    )
