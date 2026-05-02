"""
System endpoints - System state management
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.system_state import (
    SystemStateResponse, UpdateSystemStateRequest, UpdateSystemStateResponse
)
from app.services.system_state_service import SystemStateService
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.core.logging import logger


router = APIRouter()


@router.get(
    "/state",
    response_model=SystemStateResponse,
    summary="Get current system state",
    description="Get the current global system state (mode, last updated by, etc.)"
)
async def get_system_state(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current system state
    
    Returns the current global system state including:
    - Current mode
    - Last updated by (user)
    - Junction ID (if applicable)
    - Timestamps
    
    Requires authentication.
    """
    system_state_service = SystemStateService(db)
    state_details = await system_state_service.get_state_with_details()
    
    return SystemStateResponse(**state_details)


@router.post(
    "/mode/{mode}",
    response_model=UpdateSystemStateResponse,
    summary="Update system mode",
    description="Update the global system mode (admin only)"
)
async def update_system_mode(
    mode: str,
    request: UpdateSystemStateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Update system mode (Admin only)
    
    Updates the global system mode and tracks the change.
    
    Steps:
    1. Validate user is admin
    2. Get current system state
    3. Validate new mode
    4. Update system state
    5. Log the change
    
    Args:
        mode: New system mode (manual, auto_circle, auto_jump, blinker, vip)
        request: Additional mode configuration
    
    Returns:
        Updated system state with previous and current mode
    
    Requires admin role.
    """
    system_state_service = SystemStateService(db)
    
    # Update system state
    updated_state, previous_mode = await system_state_service.update_system_state(
        new_mode=mode,
        user_id=current_user.id,
        junction_id=request.junction_id,
        mode_metadata=request.mode_metadata
    )
    
    # Get state with details
    state_details = await system_state_service.get_state_with_details()
    
    logger.info(
        f"System mode changed: {previous_mode} → {mode} by {current_user.email}",
        extra={
            "user_id": current_user.id,
            "user_email": current_user.email,
            "previous_mode": previous_mode,
            "new_mode": mode,
            "junction_id": request.junction_id
        }
    )
    
    return UpdateSystemStateResponse(
        success=True,
        message=f"System mode updated from '{previous_mode}' to '{mode}'",
        previous_mode=previous_mode,
        current_mode=mode,
        system_state=SystemStateResponse(**state_details)
    )


@router.post(
    "/mode",
    response_model=UpdateSystemStateResponse,
    summary="Update system mode (body)",
    description="Update the global system mode using request body (admin only)"
)
async def update_system_mode_body(
    request: UpdateSystemStateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Update system mode using request body (Admin only)
    
    Alternative endpoint that accepts mode in request body instead of path.
    
    Args:
        request: Mode update request with new_mode and optional configuration
    
    Returns:
        Updated system state with previous and current mode
    
    Requires admin role.
    """
    system_state_service = SystemStateService(db)
    
    # Update system state
    updated_state, previous_mode = await system_state_service.update_system_state(
        new_mode=request.new_mode,
        user_id=current_user.id,
        junction_id=request.junction_id,
        mode_metadata=request.mode_metadata
    )
    
    # Get state with details
    state_details = await system_state_service.get_state_with_details()
    
    logger.info(
        f"System mode changed: {previous_mode} → {request.new_mode} by {current_user.email}",
        extra={
            "user_id": current_user.id,
            "user_email": current_user.email,
            "previous_mode": previous_mode,
            "new_mode": request.new_mode,
            "junction_id": request.junction_id
        }
    )
    
    return UpdateSystemStateResponse(
        success=True,
        message=f"System mode updated from '{previous_mode}' to '{request.new_mode}'",
        previous_mode=previous_mode,
        current_mode=request.new_mode,
        system_state=SystemStateResponse(**state_details)
    )


@router.post(
    "/reset",
    response_model=UpdateSystemStateResponse,
    summary="Reset system to default mode",
    description="Reset the system to default manual mode (admin only)"
)
async def reset_system_mode(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Reset system to default mode (Admin only)
    
    Resets the system to manual mode (default state).
    
    Returns:
        Updated system state with previous and current mode
    
    Requires admin role.
    """
    system_state_service = SystemStateService(db)
    
    # Reset to default
    updated_state, previous_mode = await system_state_service.reset_to_default(
        user_id=current_user.id
    )
    
    # Get state with details
    state_details = await system_state_service.get_state_with_details()
    
    logger.info(
        f"System reset to default: {previous_mode} → manual by {current_user.email}",
        extra={
            "user_id": current_user.id,
            "user_email": current_user.email,
            "previous_mode": previous_mode
        }
    )
    
    return UpdateSystemStateResponse(
        success=True,
        message=f"System reset to default mode from '{previous_mode}'",
        previous_mode=previous_mode,
        current_mode="manual",
        system_state=SystemStateResponse(**state_details)
    )


@router.get(
    "/mode",
    response_model=dict,
    summary="Get current mode only",
    description="Get just the current system mode string"
)
async def get_current_mode(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current mode only
    
    Returns just the current mode string for quick checks.
    
    Requires authentication.
    """
    system_state_service = SystemStateService(db)
    current_mode = await system_state_service.get_current_mode()
    
    return {
        "current_mode": current_mode
    }
