"""
Authentication service - Business logic for authentication
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, Session, UserRole, UserStatus
from app.schemas.auth import (
    LoginRequest, RegisterRequest, TokenResponse, 
    RefreshTokenRequest, PasswordChangeRequest
)
from app.core.security import (
    hash_password, verify_password, 
    create_access_token, create_refresh_token, decode_token
)
from app.core.config import settings
from app.core.exceptions import (
    AuthenticationException, ValidationException, 
    NotFoundException, AccountLockedException
)
from app.core.logging import logger


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(
        self, 
        register_data: RegisterRequest,
        created_by_admin: bool = False
    ) -> User:
        """
        Register a new user
        
        Args:
            register_data: Registration data
            created_by_admin: Whether user is being created by admin
        
        Returns:
            Created user
        
        Raises:
            ValidationException: If email already exists or invalid role
        """
        # Check if email already exists
        result = await self.db.execute(
            select(User).where(User.email == register_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ValidationException(detail="Email already registered")
        
        # Validate role
        try:
            role = UserRole(register_data.role.lower())
        except ValueError:
            raise ValidationException(detail=f"Invalid role: {register_data.role}")
        
        # Only admins can create admin users
        if role == UserRole.ADMIN and not created_by_admin:
            raise ValidationException(detail="Cannot register as admin")
        
        # Hash password
        password_hash = hash_password(register_data.password)
        
        # Create user
        user = User(
            name=register_data.name,
            email=register_data.email,
            password_hash=password_hash,
            role=role,
            status=UserStatus.ACTIVE
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info(f"User registered: {user.email} (role: {user.role})")
        
        return user
    
    async def authenticate(
        self, 
        login_data: LoginRequest,
        ip_address: str,
        user_agent: str
    ) -> Tuple[User, TokenResponse]:
        """
        Authenticate user and generate tokens
        
        Args:
            login_data: Login credentials
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Tuple of (User, TokenResponse)
        
        Raises:
            AuthenticationException: If credentials are invalid
            AccountLockedException: If account is locked
        """
        # Get user by email
        result = await self.db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"Login attempt with non-existent email: {login_data.email}")
            raise AuthenticationException(detail="Invalid email or password")
        
        # Check if account is locked
        if user.status == UserStatus.LOCKED:
            if user.locked_until and user.locked_until > datetime.utcnow():
                remaining = (user.locked_until - datetime.utcnow()).seconds // 60
                raise AccountLockedException(
                    detail=f"Account locked. Try again in {remaining} minutes"
                )
            else:
                # Unlock account if lock period has passed
                user.status = UserStatus.ACTIVE
                user.failed_login_attempts = 0
                user.locked_until = None
        
        # Check if account is inactive
        if user.status == UserStatus.INACTIVE:
            raise AuthenticationException(detail="Account is inactive")
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            # Increment failed login attempts
            user.failed_login_attempts += 1
            
            # Lock account if max attempts reached
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.status = UserStatus.LOCKED
                user.locked_until = datetime.utcnow() + timedelta(
                    minutes=settings.LOCKOUT_DURATION_MINUTES
                )
                await self.db.commit()
                
                logger.warning(f"Account locked due to failed attempts: {user.email}")
                raise AccountLockedException(
                    detail=f"Account locked due to multiple failed login attempts. "
                           f"Try again in {settings.LOCKOUT_DURATION_MINUTES} minutes"
                )
            
            await self.db.commit()
            
            logger.warning(
                f"Failed login attempt for {user.email} "
                f"(attempt {user.failed_login_attempts}/{settings.MAX_LOGIN_ATTEMPTS})"
            )
            raise AuthenticationException(detail="Invalid email or password")
        
        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.last_login = datetime.utcnow()
        
        # Generate tokens
        tokens = await self._generate_tokens(user, ip_address, user_agent)
        
        await self.db.commit()
        
        logger.info(f"User logged in: {user.email} from {ip_address}")
        
        return user, tokens
    
    async def refresh_access_token(
        self, 
        refresh_data: RefreshTokenRequest,
        ip_address: str
    ) -> TokenResponse:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_data: Refresh token data
            ip_address: Client IP address
        
        Returns:
            New token response
        
        Raises:
            AuthenticationException: If refresh token is invalid
        """
        # Decode refresh token
        payload = decode_token(refresh_data.refresh_token)
        
        # Verify token type
        if payload.get("type") != "refresh":
            raise AuthenticationException(detail="Invalid token type")
        
        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException(detail="Invalid token payload")
        
        # Get session from database
        result = await self.db.execute(
            select(Session).where(
                Session.refresh_token == refresh_data.refresh_token,
                Session.is_active == True
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise AuthenticationException(detail="Invalid or expired refresh token")
        
        # Check if session is expired
        if session.expires_at < datetime.utcnow():
            session.is_active = False
            await self.db.commit()
            raise AuthenticationException(detail="Refresh token expired")
        
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user or user.status != UserStatus.ACTIVE:
            raise AuthenticationException(detail="User not found or inactive")
        
        # Update session last_seen
        session.last_seen = datetime.utcnow()
        session.ip_address = ip_address
        
        # Generate new access token (keep same refresh token)
        access_token = create_access_token({"sub": str(user.id)})
        
        await self.db.commit()
        
        logger.info(f"Access token refreshed for user: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def logout(self, refresh_token: str) -> None:
        """
        Logout user by invalidating refresh token
        
        Args:
            refresh_token: Refresh token to invalidate
        """
        result = await self.db.execute(
            select(Session).where(Session.refresh_token == refresh_token)
        )
        session = result.scalar_one_or_none()
        
        if session:
            session.is_active = False
            await self.db.commit()
            logger.info(f"User logged out: session_id={session.id}")
    
    async def change_password(
        self, 
        user: User, 
        password_data: PasswordChangeRequest
    ) -> None:
        """
        Change user password
        
        Args:
            user: Current user
            password_data: Password change data
        
        Raises:
            AuthenticationException: If current password is incorrect
        """
        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            raise AuthenticationException(detail="Current password is incorrect")
        
        # Hash new password
        user.password_hash = hash_password(password_data.new_password)
        
        # Invalidate all existing sessions (force re-login)
        result = await self.db.execute(
            select(Session).where(
                Session.user_id == user.id,
                Session.is_active == True
            )
        )
        sessions = result.scalars().all()
        
        for session in sessions:
            session.is_active = False
        
        await self.db.commit()
        
        logger.info(f"Password changed for user: {user.email}")
    
    async def _generate_tokens(
        self, 
        user: User, 
        ip_address: str, 
        user_agent: str
    ) -> TokenResponse:
        """
        Generate access and refresh tokens
        
        Args:
            user: User object
            ip_address: Client IP address
            user_agent: Client user agent
        
        Returns:
            Token response
        """
        # Create token payload
        token_data = {"sub": str(user.id)}
        
        # Generate tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Create session record
        session = Session(
            user_id=user.id,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        self.db.add(session)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
        
        Returns:
            User or None
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
        
        Returns:
            User or None
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
