import bcrypt
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union
from jose import jwt
from app.config.loader import settings

ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
REFRESH_TOKEN_EXPIRE_DAYS: int = 7

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain password matches the hashed password representation.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), 
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """
    Generates a secure bcrypt password hash of a raw string.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(
    subject: Union[str, Any], 
    role: str,
    permissions: List[str],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a signed JWT access token containing subject identity, role, and permission scopes.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode: Dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "role": role,
        "permissions": permissions,
        "jti": uuid.uuid4().hex,
        "type": "access"
    }
    encoded_jwt: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Creates a distinct JWT refresh token with a longer lifespan and unique identifier.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode: Dict[str, Any] = {
        "exp": expire,
        "sub": str(subject),
        "jti": uuid.uuid4().hex,
        "type": "refresh"
    }
    encoded_jwt: str = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token using the system key.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
