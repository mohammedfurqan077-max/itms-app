"""
SystemState service - Business logic for system state management
"""
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_state import SystemState
from app.models.user import User
from app.schemas.system_state import SystemModeEnum
from app.core.exceptions import ValidationException, NotFoundException
from app.core.logging import logger


class SystemStateService:
    """SystemState service - Singleton pattern implementation"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_system_state(self) -> SystemState:
        """
        Get the current system state (singleton)
        
        If no state exists, creates a default state.
        
        Returns:
            SystemState: Current system state
        """
        # Try to get existing state
        result = await self.db.execute(
            select(SystemState).where(SystemState.id == SystemState.get_singleton_id())
        )
        state = result.scalar_one_or_none()
        
        # If no state exists, create default
        if not state:
            state = await self._create_default_state()
            logger.info("Created default system state")
        
        return state
    
    async def update_system_state(
        self,
        new_mode: str,
        user_id: int,
        junction_id: Optional[int] = None,
        mode_metadata: Optional[str] = None
    ) -> Tuple[SystemState, str]:
        """
        Update the system state with transaction safety
        
        Args:
            new_mode: New system mode
            user_id: User ID who is updating the state
            junction_id: Optional junction ID for junction-specific modes
            mode_metadata: Optional JSON metadata for mode configuration
        
        Returns:
            Tuple of (updated_state, previous_mode)
        
        Raises:
            ValidationException: If mode is invalid
        """
        # Validate mode
        if not SystemModeEnum.is_valid(new_mode):
            raise ValidationException(
                detail=f"Invalid mode: {new_mode}. Valid modes: {', '.join(SystemModeEnum.all_modes())}"
            )
        
        # Get current state
        state = await self.get_system_state()
        
        # Store previous mode
        previous_mode = state.current_mode
        
        # Update state
        state.current_mode = new_mode
        state.last_updated_by = user_id
        state.junction_id = junction_id
        state.mode_metadata = mode_metadata
        
        # Commit changes
        await self.db.commit()
        await self.db.refresh(state)
        
        logger.info(
            f"System state updated: {previous_mode} → {new_mode} by user_id={user_id}",
            extra={
                "previous_mode": previous_mode,
                "new_mode": new_mode,
                "user_id": user_id,
                "junction_id": junction_id
            }
        )
        
        return state, previous_mode
    
    async def get_current_mode(self) -> str:
        """
        Get the current system mode
        
        Returns:
            str: Current mode
        """
        state = await self.get_system_state()
        return state.current_mode
    
    async def is_mode_active(self, mode: str) -> bool:
        """
        Check if a specific mode is currently active
        
        Args:
            mode: Mode to check
        
        Returns:
            bool: True if mode is active
        """
        current_mode = await self.get_current_mode()
        return current_mode == mode
    
    async def _create_default_state(self) -> SystemState:
        """
        Create default system state (singleton)
        
        Returns:
            SystemState: Created default state
        """
        state = SystemState(
            id=SystemState.get_singleton_id(),
            current_mode=SystemModeEnum.MANUAL,
            last_updated_by=None,
            junction_id=None,
            mode_metadata=None
        )
        
        self.db.add(state)
        await self.db.commit()
        await self.db.refresh(state)
        
        return state
    
    async def reset_to_default(self, user_id: int) -> Tuple[SystemState, str]:
        """
        Reset system state to default (manual mode)
        
        Args:
            user_id: User ID who is resetting the state
        
        Returns:
            Tuple of (updated_state, previous_mode)
        """
        return await self.update_system_state(
            new_mode=SystemModeEnum.MANUAL,
            user_id=user_id,
            junction_id=None,
            mode_metadata=None
        )
    
    async def get_state_with_details(self) -> dict:
        """
        Get system state with user and junction details
        
        Returns:
            dict: System state with nested details
        """
        state = await self.get_system_state()
        
        return {
            "id": state.id,
            "current_mode": state.current_mode,
            "last_updated_by": state.last_updated_by,
            "junction_id": state.junction_id,
            "mode_metadata": state.mode_metadata,
            "updated_at": state.updated_at,
            "created_at": state.created_at,
            "updated_by_name": state.updated_by_user.name if state.updated_by_user else None,
            "junction_name": state.junction.name if state.junction else None
        }
