"""
Control endpoints - Interface to external control system
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.session import get_db
from app.schemas.control import (
    SwitchModeRequest, SwitchModeResponse,
    SetManualTimesRequest, SetManualTimesResponse,
    VIPOverrideRequest, VIPOverrideResponse,
    ControlStatusResponse, HealthCheckResponse
)
from app.services.control_service import get_control_service, ControlService
from app.services.system_state_service import SystemStateService
from app.core.dependencies import get_current_user, require_role, require_permission
from app.models.user import User, UserRole
from app.core.logging import logger
from app.core.exceptions import JunctionException


router = APIRouter()


@router.post(
    "/switch_mode",
    response_model=SwitchModeResponse,
    summary="Switch traffic control mode",
    description="Switch the traffic control system to a different mode (admin only)"
)
async def switch_mode(
    request: SwitchModeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Switch traffic control mode
    
    Flow:
    1. Validate JWT user (done by dependency)
    2. Check role = admin (done by dependency)
    3. Get current SystemState
    4. Store previous_mode
    5. Call control_service.switch_mode(mode)
    6. If success:
       - Update SystemState with new mode
    7. Log action
    
    IMPORTANT: If control service fails, DO NOT update state.
    
    Args:
        request: Mode switch request with mode name
    
    Returns:
        Response with success status and control system data
    
    Requires admin role.
    """
    control_service = get_control_service()
    system_state_service = SystemStateService(db)
    
    # Step 3: Get current SystemState
    current_state = await system_state_service.get_system_state()
    
    # Step 4: Store previous_mode
    previous_mode = current_state.current_mode
    
    logger.info(
        f"Attempting mode switch: {previous_mode} → {request.mode}",
        extra={
            "user_id": current_user.id,
            "user_email": current_user.email,
            "previous_mode": previous_mode,
            "requested_mode": request.mode
        }
    )
    
    # Step 5: Call control_service.switch_mode(mode)
    response = await control_service.switch_mode(request.mode)
    
    # Step 6: If success, update SystemState
    if response.success:
        try:
            # Update system state with transaction safety
            await system_state_service.update_system_state(
                new_mode=request.mode,
                user_id=current_user.id
            )
            
            # Step 7: Log action (success)
            logger.info(
                f"Mode switched successfully: {previous_mode} → {request.mode} by {current_user.email}",
                extra={
                    "user_id": current_user.id,
                    "user_email": current_user.email,
                    "previous_mode": previous_mode,
                    "new_mode": request.mode,
                    "control_response": response.data
                }
            )
            
            return SwitchModeResponse(
                success=True,
                message=f"Mode switched from '{previous_mode}' to '{request.mode}' successfully",
                previous_mode=previous_mode,
                current_mode=request.mode,
                control_data=response.data,
                error=None
            )
        
        except Exception as e:
            # Rollback will happen automatically due to exception
            logger.error(
                f"Failed to update system state after successful control command: {str(e)}",
                extra={
                    "user_id": current_user.id,
                    "requested_mode": request.mode,
                    "error": str(e)
                },
                exc_info=True
            )
            
            # Return failure even though control succeeded
            # This is a critical error - control system changed but state didn't update
            return SwitchModeResponse(
                success=False,
                message="Control system updated but failed to update system state",
                previous_mode=previous_mode,
                current_mode=previous_mode,  # State wasn't updated
                control_data=response.data,
                error=f"State update failed: {str(e)}"
            )
    
    else:
        # Step 7: Log action (failure)
        # Control service failed - DO NOT update state
        logger.error(
            f"Control service failed to switch mode: {response.error}",
            extra={
                "user_id": current_user.id,
                "user_email": current_user.email,
                "requested_mode": request.mode,
                "previous_mode": previous_mode,
                "error": response.error,
                "status_code": response.status_code
            }
        )
        
        return SwitchModeResponse(
            success=False,
            message=f"Failed to switch mode: {response.message}",
            previous_mode=previous_mode,
            current_mode=previous_mode,  # State unchanged
            control_data=response.data,
            error=response.error
        )


@router.post(
    "/manual_times",
    response_model=SetManualTimesResponse,
    summary="Set manual lane timings",
    description="Set manual timing for all lanes (requires set_time permission)"
)
async def set_manual_times(
    request: SetManualTimesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("set_time"))
):
    """
    Set manual lane timings
    
    Flow:
    1. Validate JWT user (done by dependency)
    2. Check permission = set_time (done by dependency)
    3. Get current SystemState
    4. Store previous_mode
    5. Call control_service.set_manual_times()
    6. If success:
       - Update SystemState to manual mode with metadata
    7. Log action
    
    IMPORTANT: If control service fails, DO NOT update state.
    
    Args:
        request: Manual times request with lane timings
    
    Returns:
        Response with success status and applied timings
    
    Requires set_time permission.
    """
    control_service = get_control_service()
    system_state_service = SystemStateService(db)
    
    # Get current state
    current_state = await system_state_service.get_system_state()
    previous_mode = current_state.current_mode
    
    logger.info(
        f"Attempting to set manual times: L1={request.lane1}s, L2={request.lane2}s, L3={request.lane3}s, L4={request.lane4}s",
        extra={
            "user_id": current_user.id,
            "user_email": current_user.email,
            "previous_mode": previous_mode
        }
    )
    
    # Send command to control system
    response = await control_service.set_manual_times(
        lane1=request.lane1,
        lane2=request.lane2,
        lane3=request.lane3,
        lane4=request.lane4
    )
    
    if response.success:
        try:
            # Update system state to manual mode with metadata
            await system_state_service.update_system_state(
                new_mode="manual",
                user_id=current_user.id,
                mode_metadata=f'{{"lane1":{request.lane1},"lane2":{request.lane2},"lane3":{request.lane3},"lane4":{request.lane4}}}'
            )
            
            logger.info(
                f"Manual times set successfully by {current_user.email}: L1={request.lane1}s, L2={request.lane2}s, L3={request.lane3}s, L4={request.lane4}s",
                extra={
                    "user_id": current_user.id,
                    "user_email": current_user.email,
                    "previous_mode": previous_mode,
                    "lane1": request.lane1,
                    "lane2": request.lane2,
                    "lane3": request.lane3,
                    "lane4": request.lane4
                }
            )
            
            return SetManualTimesResponse(
                success=True,
                message="Manual times set successfully",
                lane1=request.lane1,
                lane2=request.lane2,
                lane3=request.lane3,
                lane4=request.lane4,
                control_data=response.data,
                error=None
            )
        
        except Exception as e:
            logger.error(
                f"Failed to update system state after successful control command: {str(e)}",
                extra={
                    "user_id": current_user.id,
                    "error": str(e)
                },
                exc_info=True
            )
            
            return SetManualTimesResponse(
                success=False,
                message="Control system updated but failed to update system state",
                lane1=request.lane1,
                lane2=request.lane2,
                lane3=request.lane3,
                lane4=request.lane4,
                control_data=response.data,
                error=f"State update failed: {str(e)}"
            )
    
    else:
        # Control service failed - DO NOT update state
        logger.error(
            f"Control service failed to set manual times: {response.error}",
            extra={
                "user_id": current_user.id,
                "user_email": current_user.email,
                "error": response.error
            }
        )
        
        return SetManualTimesResponse(
            success=False,
            message=f"Failed to set manual times: {response.message}",
            lane1=request.lane1,
            lane2=request.lane2,
            lane3=request.lane3,
            lane4=request.lane4,
            control_data=response.data,
            error=response.error
        )


@router.post(
    "/vip_override",
    response_model=VIPOverrideResponse,
    summary="VIP override mode",
    description="Activate or deactivate VIP override (requires vip_mode permission)"
)
async def vip_override(
    request: VIPOverrideRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("vip_mode"))
):
    """
    VIP override mode
    
    Flow:
    1. Validate JWT user (done by dependency)
    2. Check permission = vip_mode (done by dependency)
    3. Get current SystemState
    4. Store previous_mode
    5. Call control_service.vip_override()
    6. If success:
       - Update SystemState to vip mode (if activating)
       - Reset to default mode (if deactivating)
    7. Log action
    
    IMPORTANT: If control service fails, DO NOT update state.
    
    Args:
        request: VIP override request with active status and lanes
    
    Returns:
        Response with success status
    
    Requires vip_mode permission.
    """
    control_service = get_control_service()
    system_state_service = SystemStateService(db)
    
    # Get current state
    current_state = await system_state_service.get_system_state()
    previous_mode = current_state.current_mode
    
    action = "activate" if request.active else "deactivate"
    logger.info(
        f"Attempting to {action} VIP mode: lanes={request.lanes_to_green}",
        extra={
            "user_id": current_user.id,
            "user_email": current_user.email,
            "previous_mode": previous_mode,
            "active": request.active,
            "lanes_to_green": request.lanes_to_green
        }
    )
    
    # Send command to control system
    response = await control_service.vip_override(
        active=request.active,
        lanes_to_green=request.lanes_to_green
    )
    
    if response.success:
        try:
            if request.active:
                # Update system state to VIP mode
                await system_state_service.update_system_state(
                    new_mode="vip",
                    user_id=current_user.id,
                    mode_metadata=f'{{"lanes_to_green":{request.lanes_to_green}}}'
                )
                
                logger.info(
                    f"VIP mode activated successfully by {current_user.email}: lanes={request.lanes_to_green}",
                    extra={
                        "user_id": current_user.id,
                        "user_email": current_user.email,
                        "previous_mode": previous_mode,
                        "lanes_to_green": request.lanes_to_green
                    }
                )
            else:
                # Revert to default mode (manual)
                await system_state_service.reset_to_default(current_user.id)
                
                logger.info(
                    f"VIP mode deactivated successfully by {current_user.email}",
                    extra={
                        "user_id": current_user.id,
                        "user_email": current_user.email,
                        "previous_mode": previous_mode
                    }
                )
            
            return VIPOverrideResponse(
                success=True,
                message=f"VIP mode {'activated' if request.active else 'deactivated'} successfully",
                active=request.active,
                lanes_to_green=request.lanes_to_green,
                control_data=response.data,
                error=None
            )
        
        except Exception as e:
            logger.error(
                f"Failed to update system state after successful control command: {str(e)}",
                extra={
                    "user_id": current_user.id,
                    "error": str(e)
                },
                exc_info=True
            )
            
            return VIPOverrideResponse(
                success=False,
                message="Control system updated but failed to update system state",
                active=request.active,
                lanes_to_green=request.lanes_to_green,
                control_data=response.data,
                error=f"State update failed: {str(e)}"
            )
    
    else:
        # Control service failed - DO NOT update state
        logger.error(
            f"Control service failed to {action} VIP mode: {response.error}",
            extra={
                "user_id": current_user.id,
                "user_email": current_user.email,
                "error": response.error
            }
        )
        
        return VIPOverrideResponse(
            success=False,
            message=f"Failed to {action} VIP mode: {response.message}",
            active=request.active,
            lanes_to_green=request.lanes_to_green,
            control_data=response.data,
            error=response.error
        )


@router.get(
    "/status",
    response_model=ControlStatusResponse,
    summary="Get control system status",
    description="Get current status from the control system"
)
async def get_control_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get control system status
    
    Retrieves the current status from the external control system.
    
    Returns:
        Current status including mode, timings, and health
    
    Requires authentication.
    """
    control_service = get_control_service()
    
    response = await control_service.get_status()
    
    return ControlStatusResponse(
        success=response.success,
        message=response.message,
        status_data=response.data,
        error=response.error
    )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Check if control system is reachable"
)
async def health_check(
    current_user: User = Depends(get_current_user)
):
    """
    Health check
    
    Checks if the external control system is reachable and responding.
    
    Returns:
        Health status
    
    Requires authentication.
    """
    control_service = get_control_service()
    
    is_healthy = await control_service.health_check()
    
    return HealthCheckResponse(
        healthy=is_healthy,
        message="Control system is healthy" if is_healthy else "Control system is not responding"
    )


@router.post(
    "/emergency_stop",
    response_model=dict,
    summary="Emergency stop",
    description="Emergency stop - set all signals to safe state (admin only)"
)
async def emergency_stop(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Emergency stop
    
    Flow:
    1. Validate JWT user (done by dependency)
    2. Check role = admin (done by dependency)
    3. Get current SystemState
    4. Store previous_mode
    5. Call control_service.emergency_stop()
    6. If success:
       - Update SystemState to blinker mode
    7. Log action
    
    IMPORTANT: If control service fails, DO NOT update state.
    
    Triggers emergency stop on the control system, setting all signals
    to a safe state (typically all red or blinker).
    
    Returns:
        Response with success status
    
    Requires admin role.
    """
    control_service = get_control_service()
    system_state_service = SystemStateService(db)
    
    # Get current state
    current_state = await system_state_service.get_system_state()
    previous_mode = current_state.current_mode
    
    logger.warning(
        f"Emergency stop triggered by {current_user.email}",
        extra={
            "user_id": current_user.id,
            "user_email": current_user.email,
            "previous_mode": previous_mode
        }
    )
    
    # Send emergency stop command
    response = await control_service.emergency_stop()
    
    if response.success:
        try:
            # Update system state to blinker mode
            await system_state_service.update_system_state(
                new_mode="blinker",
                user_id=current_user.id
            )
            
            logger.warning(
                f"Emergency stop executed successfully: {previous_mode} → blinker by {current_user.email}",
                extra={
                    "user_id": current_user.id,
                    "user_email": current_user.email,
                    "previous_mode": previous_mode
                }
            )
            
            return {
                "success": True,
                "message": "Emergency stop executed successfully",
                "previous_mode": previous_mode,
                "current_mode": "blinker",
                "error": None
            }
        
        except Exception as e:
            logger.error(
                f"Failed to update system state after successful emergency stop: {str(e)}",
                extra={
                    "user_id": current_user.id,
                    "error": str(e)
                },
                exc_info=True
            )
            
            return {
                "success": False,
                "message": "Control system stopped but failed to update system state",
                "previous_mode": previous_mode,
                "current_mode": previous_mode,
                "error": f"State update failed: {str(e)}"
            }
    
    else:
        # Control service failed - DO NOT update state
        logger.error(
            f"Emergency stop failed: {response.error}",
            extra={
                "user_id": current_user.id,
                "user_email": current_user.email,
                "error": response.error
            }
        )
        
        return {
            "success": False,
            "message": f"Emergency stop failed: {response.message}",
            "previous_mode": previous_mode,
            "current_mode": previous_mode,
            "error": response.error
        }
