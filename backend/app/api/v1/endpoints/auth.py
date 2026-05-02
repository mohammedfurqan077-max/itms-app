"""
Authentication endpoints
"""
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest, LoginResponse, RegisterRequest, RegisterResponse,
    RefreshTokenRequest, TokenResponse, LogoutResponse,
    UserResponse, PasswordChangeRequest
)
from app.services.auth_service import AuthService
from app.core.dependencies import get_current_user, get_client_ip, get_user_agent
from app.models.user import User
from app.core.rate_limit import limiter
from app.core.logging import logger


router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account. Only 'jawan' role can be self-registered."
)
@limiter.limit("5/minute")
async def register(
    request: Request,
    register_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user
    
    - **name**: User's full name (2-100 characters)
    - **email**: Valid email address (must be unique)
    - **password**: Strong password (minimum 8 characters)
    - **role**: User role (default: 'jawan', only 'jawan' allowed for self-registration)
    
    Returns the created user details.
    """
    auth_service = AuthService(db)
    user = await auth_service.register(register_data, created_by_admin=False)
    
    return RegisterResponse(
        user=UserResponse.model_validate(user),
        message="User registered successfully"
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="Authenticate user and receive JWT tokens"
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
    ip_address: str = Depends(get_client_ip),
    user_agent: str = Depends(get_user_agent)
):
    """
    Authenticate user and receive tokens
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns:
    - User details
    - Access token (valid for 30 minutes)
    - Refresh token (valid for 7 days)
    
    The access token should be included in the Authorization header:
    `Authorization: Bearer <access_token>`
    """
    auth_service = AuthService(db)
    user, tokens = await auth_service.authenticate(
        login_data, 
        ip_address, 
        user_agent
    )
    
    return LoginResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get a new access token using refresh token"
)
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    ip_address: str = Depends(get_client_ip)
):
    """
    Refresh access token
    
    - **refresh_token**: Valid refresh token received during login
    
    Returns a new access token while keeping the same refresh token.
    Use this endpoint when the access token expires.
    """
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_access_token(refresh_data, ip_address)
    
    return tokens


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="User logout",
    description="Logout user and invalidate refresh token"
)
async def logout(
    refresh_token: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Logout user
    
    - **refresh_token**: Refresh token to invalidate
    
    Invalidates the refresh token, effectively logging out the user.
    The access token will still be valid until it expires.
    """
    auth_service = AuthService(db)
    await auth_service.logout(refresh_token)
    
    logger.info(f"User logged out: {current_user.email}")
    
    return LogoutResponse(message="Logged out successfully")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get current authenticated user details"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    
    Returns the details of the currently authenticated user.
    Requires valid access token in Authorization header.
    """
    return UserResponse.model_validate(current_user)


@router.post(
    "/change-password",
    response_model=dict,
    summary="Change password",
    description="Change current user's password"
)
async def change_password(
    password_data: PasswordChangeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change user password
    
    - **current_password**: Current password
    - **new_password**: New password (minimum 8 characters)
    
    Changes the user's password and invalidates all existing sessions.
    User will need to login again with the new password.
    """
    auth_service = AuthService(db)
    await auth_service.change_password(current_user, password_data)
    
    return {
        "message": "Password changed successfully. Please login again.",
        "success": True
    }


@router.post(
    "/verify-token",
    response_model=dict,
    summary="Verify token",
    description="Verify if access token is valid"
)
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """
    Verify access token
    
    Checks if the provided access token is valid.
    Returns user information if token is valid.
    """
    return {
        "valid": True,
        "user": UserResponse.model_validate(current_user)
    }
