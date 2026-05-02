"""
Command execution endpoints - API routes for command management
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_active_user, require_role, require_permission
from app.models.user import User, UserRole
from app.services.command_service import CommandService
from app.schemas.command import (
    SendCommandRequest, CommandResponse, CommandListResponse,
    CommandExecutionResult, CommandStats, RetryCommandRequest,
    CommandStatusEnum, CommandTypeEnum
)
from app.core.logging import logger
import math


router = APIRouter()


@router.post("/send", response_model=CommandExecutionResult, status_code=200)
async def send_command(
    request: SendCommandRequest,
    current_user: User = Depends(require_permission("control:execute")),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a command to a junction device
    
    **Permissions Required:** control:execute
    
    **Command Types:**
    - `set_mode`: Switch traffic mode (auto/manual/vip)
    - `set_time`: Set manual lane timings
    - `vip_mode`: Enable/disable VIP override
    - `emergency_stop`: Emergency stop all lanes
    - `heartbeat`: Check device connectivity
    - `get_status`: Get current device status
    
    **Payload Examples:**
    
    SET_MODE:
    ```json
    {
        "command_type": "set_mode",
        "junction_id": 1,
        "payload": {"mode": "auto"}
    }
    ```
    
    SET_TIME:
    ```json
    {
        "command_type": "set_time",
        "junction_id": 1,
        "payload": {
            "lane1": 30,
            "lane2": 30,
            "lane3": 30,
            "lane4": 30
        }
    }
    ```
    
    VIP_MODE:
    ```json
    {
        "command_type": "vip_mode",
        "junction_id": 1,
        "payload": {
            "active": true,
            "lanes_to_green": [1, 3]
        }
    }
    ```
    """
    service = CommandService(db)
    
    logger.info(
        f"Sending command: {request.command_type}",
        extra={
            "command_type": request.command_type,
            "junction_id": request.junction_id,
            "user_id": current_user.id
        }
    )
    
    result = await service.send_command(request, current_user.id)
    
    return result


@router.get("/{command_id}", response_model=CommandResponse, status_code=200)
async def get_command(
    command_id: int = Path(..., description="Command ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get command details by ID
    
    **Permissions Required:** Authenticated user
    
    Returns complete command information including:
    - Command type and payload
    - Execution status
    - Response data
    - Timestamps
    - Retry information
    """
    service = CommandService(db)
    command = await service.get_command_by_id(command_id)
    
    return CommandResponse.model_validate(command)


@router.get("", response_model=CommandListResponse, status_code=200)
async def list_commands(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    junction_id: Optional[int] = Query(None, description="Filter by junction ID"),
    command_type: Optional[str] = Query(None, description="Filter by command type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List commands with pagination and filtering
    
    **Permissions Required:** Authenticated user
    
    **Filters:**
    - `junction_id`: Filter by specific junction
    - `command_type`: Filter by command type (set_mode, set_time, etc.)
    - `status`: Filter by status (pending, success, failed, etc.)
    
    **Pagination:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 10, max: 100)
    
    Returns paginated list of commands with total count and page information.
    """
    service = CommandService(db)
    
    # Validate filters
    if command_type and not CommandTypeEnum.is_valid(command_type):
        from app.core.exceptions import ValidationException
        raise ValidationException(
            detail=f"Invalid command type. Must be one of: {', '.join(CommandTypeEnum.all_types())}"
        )
    
    if status and not CommandStatusEnum.is_valid(status):
        from app.core.exceptions import ValidationException
        raise ValidationException(
            detail=f"Invalid status. Must be one of: {', '.join(CommandStatusEnum.all_statuses())}"
        )
    
    # Get commands
    commands, total = await service.get_commands(
        page=page,
        page_size=page_size,
        junction_id=junction_id,
        command_type=command_type,
        status=status
    )
    
    # Convert to response models
    command_responses = [CommandResponse.model_validate(cmd) for cmd in commands]
    
    # Calculate total pages
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return CommandListResponse(
        commands=command_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("/{command_id}/retry", response_model=CommandExecutionResult, status_code=200)
async def retry_command(
    command_id: int = Path(..., description="Command ID"),
    request: RetryCommandRequest = RetryCommandRequest(),
    current_user: User = Depends(require_permission("control:execute")),
    db: AsyncSession = Depends(get_db)
):
    """
    Retry a failed command
    
    **Permissions Required:** control:execute
    
    **Retry Logic:**
    - Only failed commands can be retried
    - Default max retries: 3
    - Use `force: true` to retry even if max retries reached
    
    **Request Body:**
    ```json
    {
        "force": false
    }
    ```
    
    Returns execution result of the retry attempt.
    """
    service = CommandService(db)
    
    logger.info(
        f"Retrying command: {command_id}",
        extra={
            "command_id": command_id,
            "force": request.force,
            "user_id": current_user.id
        }
    )
    
    result = await service.retry_command(command_id, request.force)
    
    return result


@router.post("/{command_id}/cancel", response_model=CommandResponse, status_code=200)
async def cancel_command(
    command_id: int = Path(..., description="Command ID"),
    current_user: User = Depends(require_permission("control:execute")),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a pending command
    
    **Permissions Required:** control:execute
    
    **Cancellation Rules:**
    - Only pending commands can be cancelled
    - Executing or completed commands cannot be cancelled
    
    Returns the cancelled command details.
    """
    service = CommandService(db)
    
    logger.info(
        f"Cancelling command: {command_id}",
        extra={
            "command_id": command_id,
            "user_id": current_user.id
        }
    )
    
    command = await service.cancel_command(command_id)
    
    return CommandResponse.model_validate(command)


@router.get("/stats/overview", response_model=CommandStats, status_code=200)
async def get_command_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get command execution statistics
    
    **Permissions Required:** Authenticated user
    
    **Statistics Include:**
    - Total commands
    - Commands by status (pending, success, failed, etc.)
    - Commands by type
    - Commands by junction
    - Average execution time
    
    Useful for monitoring system health and command execution patterns.
    """
    service = CommandService(db)
    stats = await service.get_command_stats()
    
    return stats


@router.get("/pending/list", response_model=list[CommandResponse], status_code=200)
async def get_pending_commands(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of commands to return"),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pending commands for execution
    
    **Permissions Required:** Admin only
    
    **Use Case:**
    - Background job processing
    - Manual command queue inspection
    - System monitoring
    
    Returns list of pending commands ordered by creation time (oldest first).
    """
    service = CommandService(db)
    commands = await service.get_pending_commands(limit)
    
    return [CommandResponse.model_validate(cmd) for cmd in commands]
