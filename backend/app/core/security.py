"""
Security utilities: password hashing, JWT tokens
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from jose import JWTError, jwt
from app.core.config import settings
from app.core.exceptions import AuthenticationException


# VALIDATE PASSWORD
def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password meets requirements.
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 72:
        return False, "Password must be at most 72 characters long"
    
    # Check byte length for bcrypt compatibility
    password_bytes = password.encode("utf-8", errors="ignore")
    if len(password_bytes) > 72:
        return False, f"Password is too long when encoded ({len(password_bytes)} bytes). Maximum is 72 bytes."
    
    return True, None


# HASH PASSWORD
def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.
    Automatically truncates to 72 bytes for bcrypt compatibility.
    """
    # Encode password to bytes and truncate to 72 bytes
    password_bytes = password.encode("utf-8", errors="ignore")[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode("utf-8")


# VERIFY PASSWORD
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.
    Automatically truncates to 72 bytes to match hashing behavior.
    """
    try:
        # Encode password to bytes and truncate to 72 bytes
        password_bytes = plain_password.encode("utf-8", errors="ignore")[:72]
        hashed_bytes = hashed_password.encode("utf-8")
        
        # Verify password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


# CREATE ACCESS TOKEN
def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()

    expire = (
        datetime.utcnow() + expires_delta
        if expires_delta
        else datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# CREATE REFRESH TOKEN
def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# DECODE TOKEN
def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise AuthenticationException(detail=f"Invalid token: {str(e)}")


# VERIFY TOKEN TYPE
def verify_token_type(payload: Dict[str, Any], expected_type: str) -> None:
    token_type = payload.get("type")

    if token_type != expected_type:
        raise AuthenticationException(
            detail=f"Invalid token type. Expected {expected_type}, got {token_type}"
        )
