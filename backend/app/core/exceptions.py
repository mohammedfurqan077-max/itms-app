"""
Custom exception classes
"""
from fastapi import status


class ITMSException(Exception):
    """Base exception for ITMS"""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST, error_code: str = None):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code or "ITMS_ERROR"
        super().__init__(self.detail)


class AuthenticationException(ITMSException):
    """Authentication related exceptions"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_ERROR"
        )


class AuthorizationException(ITMSException):
    """Authorization/Permission related exceptions"""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="PERMISSION_DENIED"
        )


class NotFoundException(ITMSException):
    """Resource not found exceptions"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND"
        )


class ValidationException(ITMSException):
    """Business logic validation exceptions"""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR"
        )


class JunctionException(ITMSException):
    """Junction communication exceptions"""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="JUNCTION_ERROR"
        )


class RateLimitException(ITMSException):
    """Rate limit exceeded exceptions"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED"
        )


class AccountLockedException(ITMSException):
    """Account locked due to failed login attempts"""
    def __init__(self, detail: str = "Account locked due to multiple failed login attempts"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_423_LOCKED,
            error_code="ACCOUNT_LOCKED"
        )


class DuplicateException(ITMSException):
    """Duplicate resource exception"""
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE"
        )
