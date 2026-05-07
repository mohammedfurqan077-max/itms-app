"""
FastAPI dependencies for authentication and authorization
"""
from typing import Optional
from fastapi import Depends, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.security import decode_token, verify_token_type
from app.core.exceptions import AuthenticationException, AuthorizationException
from app.models.user import User, UserRole
from app.services.user_service import UserService


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token
        db: Database session
    
    Returns:
        Current user object
    
    Raises:
        AuthenticationException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    verify_token_type(payload, "access")
    
    # Extract user ID
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise AuthenticationException(detail="Invalid token payload")
    
    # Get user from database
    user_service = UserService(db)
    user = await user_service.get_user_by_id(int(user_id))
    
    if user is None:
        raise AuthenticationException(detail="User not found")
    
    if user.status != "active":
        raise AuthenticationException(detail="User account is inactive")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (additional check)
    
    Args:
        current_user: Current user from token
    
    Returns:
        Current active user
    """
    if current_user.status != "active":
        raise AuthenticationException(detail="User account is inactive")
    return current_user


def require_role(required_role: str):
    """
    Dependency factory to require specific user role
    
    Args:
        required_role: Required user role (string constant from UserRole)
    
    Returns:
        Dependency function
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role:
            raise AuthorizationException(detail=f"Role '{required_role}' required")
        return current_user
    
    return role_checker


def require_permission(permission: str):
    """
    Dependency factory to require specific permission
    
    Args:
        permission: Required permission name
    
    Returns:
        Dependency function
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # Admin has all permissions
        if current_user.role == UserRole.ADMIN:
            return current_user
        
        # Check if user has the required permission
        user_service = UserService(db)
        has_permission = await user_service.user_has_permission(current_user.id, permission)
        
        if not has_permission:
            raise AuthorizationException(detail=f"Permission '{permission}' required")
        
        return current_user
    
    return permission_checker


async def get_client_ip(request: Request) -> str:
    """
    Extract client IP address from request
    
    Args:
        request: FastAPI request object
    
    Returns:
        Client IP address
    """
    # Check for forwarded IP (behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Check for real IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client
    return request.client.host if request.client else "unknown"


async def get_user_agent(user_agent: Optional[str] = Header(None)) -> str:
    """
    Extract user agent from request headers
    
    Args:
        user_agent: User-Agent header
    
    Returns:
        User agent string
    """
    return user_agent or "unknown"
