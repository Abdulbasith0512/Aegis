import logging
from datetime import datetime, timezone, timedelta
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

from app.core.dependencies import get_db, get_cache, get_current_user, get_token_payload, oauth2_scheme
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.exceptions import AuthenticationException
from app.schemas.auth import Token, LoginRequest, RefreshRequest, TokenPayload
from app.schemas.user import UserOut
from app.repositories.user import UserRepository
from app.repositories.audit import AuditRepository
from app.models.users import User

logger = logging.getLogger("aegisai.api.auth")

router: APIRouter = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Verifies user credentials and returns signed JWT access and refresh tokens.
    """
    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)
    
    user = await user_repo.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user.hashed_password):
        # Log failed login attempt
        await audit_repo.log_action(
            action_type="login_failed",
            description=f"Failed login attempt for email: {payload.email}",
            metadata={"email": payload.email}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password credentials."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    # Compile user permissions list
    permissions = [p.name for p in user.role.permissions]

    # Generate tokens
    access_token = create_access_token(
        subject=user.email,
        role=user.role.name,
        permissions=permissions
    )
    refresh_token = create_refresh_token(subject=user.email)

    # Log successful login action
    await audit_repo.log_action(
        actor_id=user.id,
        action_type="login_success",
        description=f"User {user.email} successfully logged in.",
        metadata={"role": user.role.name}
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    raw_token: str = Depends(oauth2_scheme),
    payload: TokenPayload = Depends(get_token_payload),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_cache),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Revokes the current access token by storing its JTI in the Redis blacklist.
    """
    audit_repo = AuditRepository(db)
    
    # Calculate token remaining lifespan (TTL) in seconds
    now_ts = int(datetime.now(timezone.utc).timestamp())
    remaining_ttl = max(1, payload.exp - now_ts) if payload.exp else (ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    # Write JTI to Redis blacklist
    await redis.setex(name=f"blacklist:{payload.jti}", time=remaining_ttl, value="true")

    # Audit the event
    await audit_repo.log_action(
        actor_id=current_user.id,
        action_type="logout",
        description=f"User {current_user.email} logged out. Token revoked."
    )

@router.post("/refresh", response_model=Token)
async def refresh(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_cache)
) -> Token:
    """
    Issues new access and refresh token pairs using a valid refresh token.
    """
    user_repo = UserRepository(db)
    audit_repo = AuditRepository(db)
    
    try:
        token_data = decode_token(payload.refresh_token)
        jti = token_data.get("jti")
        sub = token_data.get("sub")
        token_type = token_data.get("type")
        
        if not jti or not sub or token_type != "refresh":
            raise AuthenticationException("Invalid refresh token credentials.")
            
        # Ensure refresh token is not blacklisted
        is_revoked = await redis.exists(f"blacklist:{jti}")
        if is_revoked:
            raise AuthenticationException("Refresh token has been revoked.")
            
        user = await user_repo.get_user_by_email(sub)
        if not user or not user.is_active:
            raise AuthenticationException("Active user not found.")

        # Revoke the used refresh token JTI immediately (Rotation)
        exp = token_data.get("exp")
        now_ts = int(datetime.now(timezone.utc).timestamp())
        remaining_ttl = max(1, exp - now_ts) if exp else (7 * 24 * 3600)
        await redis.setex(name=f"blacklist:{jti}", time=remaining_ttl, value="true")

        # Create new tokens
        permissions = [p.name for p in user.role.permissions]
        new_access_token = create_access_token(
            subject=user.email,
            role=user.role.name,
            permissions=permissions
        )
        new_refresh_token = create_refresh_token(subject=user.email)

        # Audit rotation
        await audit_repo.log_action(
            actor_id=user.id,
            action_type="token_refresh",
            description=f"Access token rotated for {user.email}."
        )

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token."
        )

@router.get("/profile", response_model=UserOut)
async def get_profile(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Returns profile information of the currently authenticated user.
    """
    return current_user
