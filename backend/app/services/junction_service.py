"""
Junction service - Business logic for junction management
"""
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.junction import Junction, JunctionStatus
from app.schemas.junction import (
    JunctionCreate, JunctionUpdate, JunctionStatusUpdate,
    JunctionHeartbeat, JunctionStats
)
from app.core.exceptions import (
    ValidationException, NotFoundException, DuplicateException
)
from app.core.logging import logger


class JunctionService:
    """Junction service for managing traffic junctions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_junction(self, junction_data: JunctionCreate) -> Junction:
        """
        Create a new junction
        
        Args:
            junction_data: Junction creation data
        
        Returns:
            Created junction
        
        Raises:
            DuplicateException: If junction name or IP already exists
        """
        # Check for duplicate name
        result = await self.db.execute(
            select(Junction).where(Junction.name == junction_data.name)
        )
        if result.scalar_one_or_none():
            raise DuplicateException(detail=f"Junction with name '{junction_data.name}' already exists")
        
        # Check for duplicate IP address
        result = await self.db.execute(
            select(Junction).where(Junction.ip_address == junction_data.ip_address)
        )
        if result.scalar_one_or_none():
            raise DuplicateException(detail=f"Junction with IP address '{junction_data.ip_address}' already exists")
        
        # Check for duplicate device_id if provided
        if junction_data.device_id:
            result = await self.db.execute(
                select(Junction).where(Junction.device_id == junction_data.device_id)
            )
            if result.scalar_one_or_none():
                raise DuplicateException(detail=f"Junction with device_id '{junction_data.device_id}' already exists")
        
        # Create junction
        junction = Junction(
            name=junction_data.name,
            location=junction_data.location,
            ip_address=junction_data.ip_address,
            device_id=junction_data.device_id,
            description=junction_data.description,
            zone=junction_data.zone,
            config_metadata=junction_data.config_metadata,
            status=JunctionStatus.OFFLINE  # Default to offline until first heartbeat
        )
        
        self.db.add(junction)
        await self.db.commit()
        await self.db.refresh(junction)
        
        logger.info(
            f"Junction created: {junction.name} (ID: {junction.id})",
            extra={
                "junction_id": junction.id,
                "junction_name": junction.name,
                "ip_address": junction.ip_address
            }
        )
        
        return junction
    
    async def get_junction_by_id(self, junction_id: int) -> Junction:
        """
        Get junction by ID
        
        Args:
            junction_id: Junction ID
        
        Returns:
            Junction object
        
        Raises:
            NotFoundException: If junction not found
        """
        result = await self.db.execute(
            select(Junction).where(Junction.id == junction_id)
        )
        junction = result.scalar_one_or_none()
        
        if not junction:
            raise NotFoundException(detail=f"Junction with ID {junction_id} not found")
        
        return junction
    
    async def get_junctions(
        self,
        page: int = 1,
        page_size: int = 10,
        status: Optional[str] = None,
        zone: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Junction], int]:
        """
        Get paginated list of junctions with optional filtering
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            status: Filter by status
            zone: Filter by zone
            search: Search in name, location, or IP address
        
        Returns:
            Tuple of (junctions list, total count)
        """
        # Build query
        query = select(Junction)
        
        # Apply filters
        filters = []
        
        if status:
            filters.append(Junction.status == status)
        
        if zone:
            filters.append(Junction.zone == zone)
        
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Junction.name.ilike(search_pattern),
                    Junction.location.ilike(search_pattern),
                    Junction.ip_address.ilike(search_pattern)
                )
            )
        
        if filters:
            query = query.where(*filters)
        
        # Get total count
        count_query = select(func.count()).select_from(Junction)
        if filters:
            count_query = count_query.where(*filters)
        
        result = await self.db.execute(count_query)
        total = result.scalar()
        
        # Apply pagination
        query = query.order_by(Junction.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await self.db.execute(query)
        junctions = result.scalars().all()
        
        return list(junctions), total
    
    async def update_junction(
        self,
        junction_id: int,
        junction_data: JunctionUpdate
    ) -> Junction:
        """
        Update junction
        
        Args:
            junction_id: Junction ID
            junction_data: Junction update data
        
        Returns:
            Updated junction
        
        Raises:
            NotFoundException: If junction not found
            DuplicateException: If name or IP already exists
        """
        # Get junction
        junction = await self.get_junction_by_id(junction_id)
        
        # Check for duplicate name if changing
        if junction_data.name and junction_data.name != junction.name:
            result = await self.db.execute(
                select(Junction).where(
                    Junction.name == junction_data.name,
                    Junction.id != junction_id
                )
            )
            if result.scalar_one_or_none():
                raise DuplicateException(detail=f"Junction with name '{junction_data.name}' already exists")
        
        # Check for duplicate IP if changing
        if junction_data.ip_address and junction_data.ip_address != junction.ip_address:
            result = await self.db.execute(
                select(Junction).where(
                    Junction.ip_address == junction_data.ip_address,
                    Junction.id != junction_id
                )
            )
            if result.scalar_one_or_none():
                raise DuplicateException(detail=f"Junction with IP address '{junction_data.ip_address}' already exists")
        
        # Check for duplicate device_id if changing
        if junction_data.device_id and junction_data.device_id != junction.device_id:
            result = await self.db.execute(
                select(Junction).where(
                    Junction.device_id == junction_data.device_id,
                    Junction.id != junction_id
                )
            )
            if result.scalar_one_or_none():
                raise DuplicateException(detail=f"Junction with device_id '{junction_data.device_id}' already exists")
        
        # Update fields
        update_data = junction_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(junction, field, value)
        
        await self.db.commit()
        await self.db.refresh(junction)
        
        logger.info(
            f"Junction updated: {junction.name} (ID: {junction.id})",
            extra={
                "junction_id": junction.id,
                "junction_name": junction.name,
                "updated_fields": list(update_data.keys())
            }
        )
        
        return junction
    
    async def delete_junction(self, junction_id: int) -> None:
        """
        Delete junction
        
        Args:
            junction_id: Junction ID
        
        Raises:
            NotFoundException: If junction not found
        """
        junction = await self.get_junction_by_id(junction_id)
        
        await self.db.delete(junction)
        await self.db.commit()
        
        logger.info(
            f"Junction deleted: {junction.name} (ID: {junction.id})",
            extra={
                "junction_id": junction.id,
                "junction_name": junction.name
            }
        )
    
    async def update_junction_status(
        self,
        junction_id: int,
        status_data: JunctionStatusUpdate
    ) -> Junction:
        """
        Update junction status
        
        Args:
            junction_id: Junction ID
            status_data: Status update data
        
        Returns:
            Updated junction
        """
        junction = await self.get_junction_by_id(junction_id)
        
        old_status = junction.status
        junction.status = status_data.status
        junction.last_seen = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(junction)
        
        logger.info(
            f"Junction status updated: {junction.name} ({old_status} → {status_data.status})",
            extra={
                "junction_id": junction.id,
                "junction_name": junction.name,
                "old_status": old_status,
                "new_status": status_data.status
            }
        )
        
        return junction
    
    async def process_heartbeat(
        self,
        heartbeat_data: JunctionHeartbeat
    ) -> Junction:
        """
        Process heartbeat from junction device
        
        Args:
            heartbeat_data: Heartbeat data from device
        
        Returns:
            Updated junction
        
        Raises:
            NotFoundException: If junction not found
        """
        # Find junction by device_id
        result = await self.db.execute(
            select(Junction).where(Junction.device_id == heartbeat_data.device_id)
        )
        junction = result.scalar_one_or_none()
        
        if not junction:
            raise NotFoundException(detail=f"Junction with device_id '{heartbeat_data.device_id}' not found")
        
        # Update status and last_seen
        old_status = junction.status
        junction.status = heartbeat_data.status
        junction.last_seen = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(junction)
        
        if old_status != heartbeat_data.status:
            logger.info(
                f"Junction heartbeat: {junction.name} ({old_status} → {heartbeat_data.status})",
                extra={
                    "junction_id": junction.id,
                    "junction_name": junction.name,
                    "device_id": heartbeat_data.device_id,
                    "old_status": old_status,
                    "new_status": heartbeat_data.status
                }
            )
        
        return junction
    
    async def get_junction_stats(self) -> JunctionStats:
        """
        Get junction statistics
        
        Returns:
            Junction statistics
        """
        # Total junctions
        result = await self.db.execute(select(func.count()).select_from(Junction))
        total = result.scalar()
        
        # Count by status
        result = await self.db.execute(
            select(Junction.status, func.count())
            .group_by(Junction.status)
        )
        status_counts = dict(result.all())
        
        # Count by zone
        result = await self.db.execute(
            select(Junction.zone, func.count())
            .where(Junction.zone.isnot(None))
            .group_by(Junction.zone)
        )
        zone_counts = dict(result.all())
        
        return JunctionStats(
            total_junctions=total,
            online_junctions=status_counts.get(JunctionStatus.ONLINE, 0),
            offline_junctions=status_counts.get(JunctionStatus.OFFLINE, 0),
            maintenance_junctions=status_counts.get(JunctionStatus.MAINTENANCE, 0),
            error_junctions=status_counts.get(JunctionStatus.ERROR, 0),
            junctions_by_zone=zone_counts
        )
    
    async def check_offline_junctions(self, timeout_minutes: int = 5) -> List[Junction]:
        """
        Check for junctions that haven't sent heartbeat recently
        
        Args:
            timeout_minutes: Minutes without heartbeat to consider offline
        
        Returns:
            List of potentially offline junctions
        """
        timeout_threshold = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        
        result = await self.db.execute(
            select(Junction).where(
                Junction.status == JunctionStatus.ONLINE,
                Junction.last_seen < timeout_threshold
            )
        )
        
        return list(result.scalars().all())
