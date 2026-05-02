"""
User service - Business logic for user management
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, Permission, UserPermission
from app.core.exceptions import NotFoundException


class UserService:
    """User service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
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
    
    async def user_has_permission(self, user_id: int, permission_name: str) -> bool:
        """
        Check if user has a specific permission
        
        Args:
            user_id: User ID
            permission_name: Permission name
        
        Returns:
            True if user has permission, False otherwise
        """
        result = await self.db.execute(
            select(UserPermission)
            .join(Permission)
            .where(
                UserPermission.user_id == user_id,
                Permission.name == permission_name
            )
        )
        permission = result.scalar_one_or_none()
        return permission is not None
    
    async def get_user_permissions(self, user_id: int) -> List[Permission]:
        """
        Get all permissions for a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of permissions
        """
        result = await self.db.execute(
            select(Permission)
            .join(UserPermission)
            .where(UserPermission.user_id == user_id)
        )
        return list(result.scalars().all())
    
    async def add_permission_to_user(self, user_id: int, permission_name: str) -> None:
        """
        Add permission to user
        
        Args:
            user_id: User ID
            permission_name: Permission name
        
        Raises:
            NotFoundException: If user or permission not found
        """
        # Check if user exists
        user = await self.get_user_by_id(user_id)
        if not user:
            raise NotFoundException(detail="User not found")
        
        # Get permission
        result = await self.db.execute(
            select(Permission).where(Permission.name == permission_name)
        )
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise NotFoundException(detail=f"Permission '{permission_name}' not found")
        
        # Check if user already has permission
        has_permission = await self.user_has_permission(user_id, permission_name)
        if has_permission:
            return  # Already has permission
        
        # Add permission
        user_permission = UserPermission(
            user_id=user_id,
            permission_id=permission.id
        )
        self.db.add(user_permission)
        await self.db.commit()
    
    async def remove_permission_from_user(self, user_id: int, permission_name: str) -> None:
        """
        Remove permission from user
        
        Args:
            user_id: User ID
            permission_name: Permission name
        """
        result = await self.db.execute(
            select(UserPermission)
            .join(Permission)
            .where(
                UserPermission.user_id == user_id,
                Permission.name == permission_name
            )
        )
        user_permission = result.scalar_one_or_none()
        
        if user_permission:
            await self.db.delete(user_permission)
            await self.db.commit()
