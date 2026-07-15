import pytest
from datetime import timedelta
from jose import jwt
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    ALGORITHM
)
from app.config.loader import settings

def test_password_hashing() -> None:
    """
    Verifies password hashing encryption and matching logic.
    """
    password = "aegisai_test_password_123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_token_creation_and_decoding() -> None:
    """
    Verifies that generated JWT access tokens contain target claims and decode successfully.
    """
    email = "test@aegisai.bank"
    role = "auditor"
    permissions = ["read:transactions", "write:policies"]

    # Generate token
    token = create_access_token(
        subject=email,
        role=role,
        permissions=permissions,
        expires_delta=timedelta(minutes=5)
    )

    # Decode token
    payload = decode_token(token)
    
    assert payload.get("sub") == email
    assert payload.get("role") == role
    assert payload.get("permissions") == permissions
    assert payload.get("type") == "access"
    assert "jti" in payload
    assert "exp" in payload

def test_refresh_token_creation_and_decoding() -> None:
    """
    Verifies that generated refresh tokens contain the correct attributes.
    """
    email = "test@aegisai.bank"
    
    # Generate refresh token
    token = create_refresh_token(subject=email, expires_delta=timedelta(days=1))
    
    # Decode token
    payload = decode_token(token)
    
    assert payload.get("sub") == email
    assert payload.get("type") == "refresh"
    assert "jti" in payload
    assert "exp" in payload
