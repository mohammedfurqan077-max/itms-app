"""
Junction endpoints - API routes for junction management
"""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math

from app.db.session import get_db
from app.schemas.junction import (
    JunctionCreate, JunctionUpdate, JunctionResponse, JunctionListResponse,
    JunctionStatusUpdate, JunctionHeartbeat, JunctionStats
)
from app.services.junction_service import JunctionService
from app.core.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.core.logging import logger


router = APIRouter()


@router.post(
    "",
    response_model=JunctionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new junction",
    description="Create a new traffic junction (admin only)"
)
async def create_junction(
    junction_data: JunctionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Create a new junction
    
    - **name**: Junction name (must be unique)
    - **location**: Physical location (optional)
    - **ip_address**: IP address of controlling device (must be valid IPv4/IPv6)
    - **device_id**: Unique device identifier (optional)
    - **description**: Additional description (optional)
    - **zone**: Zone or area classification (optional)
    - **config_metadata**: JSON configuration (optional)
    
    Returns the created junction.
    
    Requires admin role.
    """
    junction_service = JunctionService(db)
    junction = await junction_service.create_junction(junction_data)
    
    logger.info(
        f"Junction created by {current_user.email}: {junction.name}",
        extra={
            "user_id": current_user.id,
            "junction_id": junction.id,
            "junction_name": junction.name
        }
    )
    
    return JunctionResponse.model_validate(junction)


@router.get(
    "",
    response_model=JunctionListResponse,
    summary="List junctions",
    description="Get paginated list of junctions with optional filtering"
)
async def list_junctions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    zone: Optional[str] = Query(None, description="Filter by zone"),
    search: Optional[str] = Query(None, description="Search in name, location, or IP"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated list of junctions
    
    Query parameters:
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    - **status**: Filter by status (online, offline, maintenance, error)
    - **zone**: Filter by zone
    - **search**: Search in name, location, or IP address
    
    Returns paginated list of junctions.
    
    Requires authentication.
    """
    junction_service = JunctionService(db)
    junctions, total = await junction_service.get_junctions(
        page=page,
        page_size=page_size,
        status=status,
        zone=zone,
        search=search
    )
    
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    
    return JunctionListResponse(
        junctions=[JunctionResponse.model_validate(j) for j in junctions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/{junction_id}",
    response_model=JunctionResponse,
    summary="Get junction by ID",
    description="Get detailed information about a specific junction"
)
async def get_junction(
    junction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get junction by ID
    
    Args:
        junction_id: Junction ID
    
    Returns junction details.
    
    Requires authentication.
    """
    junction_service = JunctionService(db)
    junction = await junction_service.get_junction_by_id(junction_id)
    
    return JunctionResponse.model_validate(junction)


@router.put(
    "/{junction_id}",
    response_model=JunctionResponse,
    summary="Update junction",
    description="Update junction information (admin only)"
)
async def update_junction(
    junction_id: int,
    junction_data: JunctionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Update junction
    
    Args:
        junction_id: Junction ID
        junction_data: Fields to update
    
    Only provided fields will be updated.
    
    Returns updated junction.
    
    Requires admin role.
    """
    junction_service = JunctionService(db)
    junction = await junction_service.update_junction(junction_id, junction_data)
    
    logger.info(
        f"Junction updated by {current_user.email}: {junction.name}",
        extra={
            "user_id": current_user.id,
            "junction_id": junction.id,
            "junction_name": junction.name
        }
    )
    
    return JunctionResponse.model_validate(junction)


@router.delete(
    "/{junction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete junction",
    description="Delete a junction (admin only)"
)
async def delete_junction(
    junction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Delete junction
    
    Args:
        junction_id: Junction ID
    
    Permanently deletes the junction.
    
    Requires admin role.
    """
    junction_service = JunctionService(db)
    junction = await junction_service.get_junction_by_id(junction_id)
    
    await junction_service.delete_junction(junction_id)
    
    logger.info(
        f"Junction deleted by {current_user.email}: {junction.name}",
        extra={
            "user_id": current_user.id,
            "junction_id": junction.id,
            "junction_name": junction.name
        }
    )


@router.patch(
    "/{junction_id}/status",
    response_model=JunctionResponse,
    summary="Update junction status",
    description="Update junction status (admin only)"
)
async def update_junction_status(
    junction_id: int,
    status_data: JunctionStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Update junction status
    
    Args:
        junction_id: Junction ID
        status_data: New status
    
    Valid statuses: online, offline, maintenance, error
    
    Returns updated junction.
    
    Requires admin role.
    """
    junction_service = JunctionService(db)
    junction = await junction_service.update_junction_status(junction_id, status_data)
    
    logger.info(
        f"Junction status updated by {current_user.email}: {junction.name} → {status_data.status}",
        extra={
            "user_id": current_user.id,
            "junction_id": junction.id,
            "junction_name": junction.name,
            "new_status": status_data.status
        }
    )
    
    return JunctionResponse.model_validate(junction)


@router.post(
    "/heartbeat",
    response_model=JunctionResponse,
    summary="Process junction heartbeat",
    description="Process heartbeat from junction device (for device communication)"
)
async def process_heartbeat(
    heartbeat_data: JunctionHeartbeat,
    db: AsyncSession = Depends(get_db)
):
    """
    Process heartbeat from junction device
    
    This endpoint is called by junction devices (Raspberry Pi) to report their status.
    
    Args:
        heartbeat_data: Heartbeat data including device_id and status
    
    Returns updated junction.
    
    Note: In production, this endpoint should be secured with device authentication.
    """
    junction_service = JunctionService(db)
    junction = await junction_service.process_heartbeat(heartbeat_data)
    
    logger.debug(
        f"Heartbeat received from junction: {junction.name}",
        extra={
            "junction_id": junction.id,
            "junction_name": junction.name,
            "device_id": heartbeat_data.device_id,
            "status": heartbeat_data.status
        }
    )
    
    return JunctionResponse.model_validate(junction)


@router.get(
    "/stats/overview",
    response_model=JunctionStats,
    summary="Get junction statistics",
    description="Get overview statistics of all junctions"
)
async def get_junction_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get junction statistics
    
    Returns:
    - Total junctions
    - Count by status (online, offline, maintenance, error)
    - Count by zone
    
    Requires authentication.
    """
    junction_service = JunctionService(db)
    stats = await junction_service.get_junction_stats()
    
    return stats


@router.get(
    "/health/check-offline",
    response_model=list[JunctionResponse],
    summary="Check offline junctions",
    description="Get list of junctions that may be offline (admin only)"
)
async def check_offline_junctions(
    timeout_minutes: int = Query(5, ge=1, le=60, description="Minutes without heartbeat"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    """
    Check for junctions that haven't sent heartbeat recently
    
    Args:
        timeout_minutes: Minutes without heartbeat to consider offline (default: 5)
    
    Returns list of potentially offline junctions.
    
    Requires admin role.
    """
    junction_service = JunctionService(db)
    offline_junctions = await junction_service.check_offline_junctions(timeout_minutes)
    
    return [JunctionResponse.model_validate(j) for j in offline_junctions]
