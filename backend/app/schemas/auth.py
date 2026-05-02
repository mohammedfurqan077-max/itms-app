"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@itms.com",
                "password": "password123"
            }
        }
    )


class RegisterRequest(BaseModel):
    """Register request schema"""
    name: str = Field(..., min_length=2, max_length=100, description="User full name")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=72, description="User password (max 72 characters)")
    role: Optional[str] = Field(default="jawan", description="User role (admin/jawan)")

    @field_validator('password')
    @classmethod
    def validate_password_bytes(cls, v: str) -> str:
        """Validate password doesn't exceed bcrypt's 72-byte limit when encoded"""
        password_bytes = v.encode("utf-8", errors="ignore")
        if len(password_bytes) > 72:
            raise ValueError(
                f"Password is too long when encoded ({len(password_bytes)} bytes). "
                f"Maximum is 72 bytes. Please use a shorter password or fewer special characters."
            )
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "email": "john@itms.com",
                "password": "SecurePass123!",
                "role": "jawan"
            }
        }
    )


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
    )


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str = Field(..., description="JWT refresh token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class UserResponse(BaseModel):
    """User response schema"""
    id: int
    name: str
    email: str
    role: str
    status: str
    last_login: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john@itms.com",
                "role": "jawan",
                "status": "active",
                "last_login": "2024-01-15T10:30:00",
                "created_at": "2024-01-01T00:00:00"
            }
        }
    )


class LoginResponse(BaseModel):
    """Login response schema"""
    user: UserResponse
    tokens: TokenResponse

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@itms.com",
                    "role": "jawan",
                    "status": "active",
                    "last_login": "2024-01-15T10:30:00",
                    "created_at": "2024-01-01T00:00:00"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800
                }
            }
        }
    )


class RegisterResponse(BaseModel):
    """Register response schema"""
    user: UserResponse
    message: str = Field(default="User registered successfully")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user": {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@itms.com",
                    "role": "jawan",
                    "status": "active",
                    "last_login": None,
                    "created_at": "2024-01-15T10:30:00"
                },
                "message": "User registered successfully"
            }
        }
    )


class LogoutResponse(BaseModel):
    """Logout response schema"""
    message: str = Field(default="Logged out successfully")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Logged out successfully"
            }
        }
    )


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""
    current_password: str = Field(..., min_length=6, description="Current password")
    new_password: str = Field(..., min_length=8, max_length=72, description="New password (max 72 characters)")

    @field_validator('new_password')
    @classmethod
    def validate_password_bytes(cls, v: str) -> str:
        """Validate password doesn't exceed bcrypt's 72-byte limit when encoded"""
        password_bytes = v.encode("utf-8", errors="ignore")
        if len(password_bytes) > 72:
            raise ValueError(
                f"Password is too long when encoded ({len(password_bytes)} bytes). "
                f"Maximum is 72 bytes. Please use a shorter password or fewer special characters."
            )
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "OldPass123!",
                "new_password": "NewSecurePass456!"
            }
        }
    )
