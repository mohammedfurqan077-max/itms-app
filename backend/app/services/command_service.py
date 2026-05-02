"""
Command service - Business logic for command execution with Raspberry Pi integration
"""
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
import json
import httpx
import asyncio

from app.models.command import Command
from app.models.junction import Junction
from app.schemas.command import (
    CommandCreate, SendCommandRequest, CommandExecutionResult,
    CommandStats, CommandTypeEnum, CommandStatusEnum
)
from app.core.config import settings
from app.core.exceptions import (
    ValidationException, NotFoundException
)
from app.core.logging import logger


class CommandService:
    """Command service for managing command execution with Raspberry Pi devices"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key = settings.CONTROL_SYSTEM_API_KEY
        self.timeout = settings.CONTROL_SYSTEM_TIMEOUT
    
    async def _get_junction(self, junction_id: int) -> Junction:
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
    
    async def _send_to_rpi(
        self,
        junction: Junction,
        endpoint: str,
        method: str = "POST",
        payload: Optional[dict] = None
    ) -> dict:
        """
        Send HTTP request to Raspberry Pi device
        
        Args:
            junction: Junction object with IP address
            endpoint: API endpoint (e.g., "/mode/auto")
            method: HTTP method (GET, POST)
            payload: Request body (for POST requests)
        
        Returns:
            Response data as dict
        
        Raises:
            Exception: If request fails
        """
        base_url = f"http://{junction.ip_address}:5000"
        url = f"{base_url}{endpoint}"
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        logger.info(
            f"Sending {method} request to RPi",
            extra={
                "junction_id": junction.id,
                "junction_name": junction.name,
                "ip_address": junction.ip_address,
                "endpoint": endpoint,
                "method": method
            }
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=payload or {})
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Raise for HTTP errors
                response.raise_for_status()
                
                # Parse response
                response_data = response.json()
                
                logger.info(
                    f"RPi request successful",
                    extra={
                        "junction_id": junction.id,
                        "status_code": response.status_code,
                        "response": response_data
                    }
                )
                
                return response_data
        
        except httpx.TimeoutException as e:
            error_msg = f"Request timeout to junction {junction.name} ({junction.ip_address})"
            logger.error(error_msg, extra={"junction_id": junction.id, "error": str(e)})
            raise Exception(error_msg)
        
        except httpx.ConnectError as e:
            error_msg = f"Connection refused by junction {junction.name} ({junction.ip_address})"
            logger.error(error_msg, extra={"junction_id": junction.id, "error": str(e)})
            raise Exception(error_msg)
        
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code} from junction {junction.name}"
            logger.error(error_msg, extra={"junction_id": junction.id, "error": str(e)})
            raise Exception(error_msg)
        
        except Exception as e:
            error_msg = f"Failed to communicate with junction {junction.name}: {str(e)}"
            logger.error(error_msg, extra={"junction_id": junction.id, "error": str(e)})
            raise Exception(error_msg)
    
    async def create_command(
        self,
        command_data: CommandCreate,
        user_id: int
    ) -> Command:
        """
        Create a new command
        
        Args:
            command_data: Command creation data
            user_id: User ID who created the command
        
        Returns:
            Created command
        """
        # Convert payload dict to JSON string
        payload_json = json.dumps(command_data.payload) if command_data.payload else None
        
        # Create command
        command = Command(
            junction_id=command_data.junction_id,
            command_type=command_data.command_type,
            payload=payload_json,
            status="pending",
            created_by=user_id,
            max_retries=command_data.max_retries or 3
        )
        
        self.db.add(command)
        await self.db.commit()
        await self.db.refresh(command)
        
        logger.info(
            f"Command created: {command.command_type} for junction {command.junction_id}",
            extra={
                "command_id": command.id,
                "command_type": command.command_type,
                "junction_id": command.junction_id,
                "user_id": user_id
            }
        )
        
        return command
    
    async def execute_command(self, command_id: int) -> CommandExecutionResult:
        """
        Execute a command on Raspberry Pi device
        
        Args:
            command_id: Command ID
        
        Returns:
            Command execution result
        """
        # Get command
        command = await self.get_command_by_id(command_id)
        
        # Check if command can be executed
        if command.is_completed():
            raise ValidationException(
                detail=f"Command {command_id} is already completed with status: {command.status}"
            )
        
        # Validate junction_id is provided
        if not command.junction_id:
            raise ValidationException(detail="Junction ID is required for command execution")
        
        # Get junction
        try:
            junction = await self._get_junction(command.junction_id)
        except NotFoundException as e:
            command.status = "failed"
            command.error_message = str(e)
            command.completed_at = datetime.utcnow()
            await self.db.commit()
            
            return CommandExecutionResult(
                command_id=command.id,
                success=False,
                message="Junction not found",
                status="failed",
                error=str(e)
            )
        
        # Update status to executing
        command.status = "executing"
        command.executed_at = datetime.utcnow()
        await self.db.commit()
        
        logger.info(
            f"Executing command: {command.command_type} on junction {junction.name}",
            extra={
                "command_id": command.id,
                "command_type": command.command_type,
                "junction_id": command.junction_id,
                "junction_name": junction.name,
                "ip_address": junction.ip_address
            }
        )
        
        try:
            # Parse payload
            payload = json.loads(command.payload) if command.payload else {}
            
            # Execute based on command type
            response_data = None
            
            if command.command_type == "set_mode":
                # POST /mode/{mode_name}
                mode = payload.get('mode')
                if not mode:
                    raise ValidationException(detail="Mode is required for SET_MODE command")
                
                endpoint = f"/mode/{mode}"
                response_data = await self._send_to_rpi(junction, endpoint, method="POST")
            
            elif command.command_type == "set_time":
                # POST /api/set_manual_times
                lane1 = payload.get('lane1')
                lane2 = payload.get('lane2')
                lane3 = payload.get('lane3')
                lane4 = payload.get('lane4')
                
                if not all([lane1, lane2, lane3, lane4]):
                    raise ValidationException(detail="All lane times are required for SET_TIME command")
                
                rpi_payload = {
                    "lane1_time": lane1,
                    "lane2_time": lane2,
                    "lane3_time": lane3,
                    "lane4_time": lane4
                }
                
                endpoint = "/api/set_manual_times"
                response_data = await self._send_to_rpi(junction, endpoint, method="POST", payload=rpi_payload)
            
            elif command.command_type == "vip_mode":
                # POST /api/vip_override
                active = payload.get('active', False)
                lanes_to_green = payload.get('lanes_to_green', [])
                
                # Convert lane numbers to string format expected by RPi (e.g., ["81", "82"])
                lanes_str = [str(lane) if isinstance(lane, int) else lane for lane in lanes_to_green]
                
                rpi_payload = {
                    "active": active,
                    "lanes_to_green": lanes_str
                }
                
                endpoint = "/api/vip_override"
                response_data = await self._send_to_rpi(junction, endpoint, method="POST", payload=rpi_payload)
            
            elif command.command_type == "emergency_stop":
                # POST /mode/emergency (assuming emergency mode exists)
                endpoint = "/mode/emergency"
                response_data = await self._send_to_rpi(junction, endpoint, method="POST")
            
            elif command.command_type == "get_status":
                # GET /status
                endpoint = "/status"
                response_data = await self._send_to_rpi(junction, endpoint, method="GET")
            
            elif command.command_type == "heartbeat":
                # GET /status (same as get_status for heartbeat)
                endpoint = "/status"
                response_data = await self._send_to_rpi(junction, endpoint, method="GET")
            
            else:
                raise ValidationException(detail=f"Unsupported command type: {command.command_type}")
            
            # Success
            command.status = "success"
            command.response = json.dumps(response_data)
            command.completed_at = datetime.utcnow()
            
            logger.info(
                f"Command executed successfully: {command.command_type}",
                extra={
                    "command_id": command.id,
                    "command_type": command.command_type,
                    "junction_id": junction.id
                }
            )
            
            result = CommandExecutionResult(
                command_id=command.id,
                success=True,
                message="Command executed successfully",
                status="success",
                response_data=response_data,
                executed_at=command.executed_at
            )
        
        except ValidationException as e:
            # Validation error
            command.status = "failed"
            command.error_message = str(e)
            command.completed_at = datetime.utcnow()
            
            logger.error(
                f"Command validation failed: {command.command_type} - {str(e)}",
                extra={
                    "command_id": command.id,
                    "command_type": command.command_type,
                    "error": str(e)
                }
            )
            
            result = CommandExecutionResult(
                command_id=command.id,
                success=False,
                message="Command validation failed",
                status="failed",
                error=str(e),
                executed_at=command.executed_at
            )
        
        except Exception as e:
            # Communication or execution error
            error_msg = str(e)
            
            # Check if it's a timeout
            if "timeout" in error_msg.lower():
                command.status = "timeout"
            else:
                command.status = "failed"
            
            command.error_message = error_msg
            command.completed_at = datetime.utcnow()
            
            logger.error(
                f"Command execution failed: {command.command_type} - {error_msg}",
                extra={
                    "command_id": command.id,
                    "command_type": command.command_type,
                    "error": error_msg
                },
                exc_info=True
            )
            
            result = CommandExecutionResult(
                command_id=command.id,
                success=False,
                message="Command execution failed",
                status=command.status,
                error=error_msg,
                executed_at=command.executed_at
            )
        
        await self.db.commit()
        await self.db.refresh(command)
        
        return result
    
    async def send_command(
        self,
        request: SendCommandRequest,
        user_id: int
    ) -> CommandExecutionResult:
        """
        Send a command (create and optionally execute immediately)
        
        Args:
            request: Send command request
            user_id: User ID who sent the command
        
        Returns:
            Command execution result
        """
        # Create command
        command_data = CommandCreate(
            junction_id=request.junction_id,
            command_type=request.command_type,
            payload=request.payload
        )
        
        command = await self.create_command(command_data, user_id)
        
        # Execute immediately if requested
        if request.execute_immediately:
            return await self.execute_command(command.id)
        else:
            return CommandExecutionResult(
                command_id=command.id,
                success=True,
                message="Command queued for execution",
                status="pending"
            )
    
    async def get_command_by_id(self, command_id: int) -> Command:
        """
        Get command by ID
        
        Args:
            command_id: Command ID
        
        Returns:
            Command object
        
        Raises:
            NotFoundException: If command not found
        """
        result = await self.db.execute(
            select(Command).where(Command.id == command_id)
        )
        command = result.scalar_one_or_none()
        
        if not command:
            raise NotFoundException(detail=f"Command with ID {command_id} not found")
        
        return command
    
    async def get_commands(
        self,
        page: int = 1,
        page_size: int = 10,
        junction_id: Optional[int] = None,
        command_type: Optional[str] = None,
        status: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Tuple[List[Command], int]:
        """
        Get paginated list of commands with optional filtering
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            junction_id: Filter by junction ID
            command_type: Filter by command type
            status: Filter by status
            user_id: Filter by user ID
        
        Returns:
            Tuple of (commands list, total count)
        """
        # Build query
        query = select(Command)
        
        # Apply filters
        filters = []
        
        if junction_id is not None:
            filters.append(Command.junction_id == junction_id)
        
        if command_type:
            filters.append(Command.command_type == command_type)
        
        if status:
            filters.append(Command.status == status)
        
        if user_id is not None:
            filters.append(Command.created_by == user_id)
        
        if filters:
            query = query.where(*filters)
        
        # Get total count
        count_query = select(func.count()).select_from(Command)
        if filters:
            count_query = count_query.where(*filters)
        
        result = await self.db.execute(count_query)
        total = result.scalar()
        
        # Apply pagination
        query = query.order_by(Command.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        result = await self.db.execute(query)
        commands = result.scalars().all()
        
        return list(commands), total
    
    async def retry_command(self, command_id: int, force: bool = False) -> CommandExecutionResult:
        """
        Retry a failed command
        
        Args:
            command_id: Command ID
            force: Force retry even if max retries reached
        
        Returns:
            Command execution result
        """
        command = await self.get_command_by_id(command_id)
        
        # Check if command can be retried
        if not command.is_failed():
            raise ValidationException(
                detail=f"Command {command_id} cannot be retried. Current status: {command.status}"
            )
        
        if not force and not command.can_retry():
            raise ValidationException(
                detail=f"Command {command_id} has reached maximum retry attempts ({command.max_retries})"
            )
        
        # Increment retry count
        command.retry_count += 1
        command.status = "pending"
        command.error_message = None
        await self.db.commit()
        
        logger.info(
            f"Retrying command: {command.command_type} (attempt {command.retry_count}/{command.max_retries})",
            extra={
                "command_id": command.id,
                "command_type": command.command_type,
                "retry_count": command.retry_count
            }
        )
        
        # Execute command
        return await self.execute_command(command_id)
    
    async def cancel_command(self, command_id: int) -> Command:
        """
        Cancel a pending command
        
        Args:
            command_id: Command ID
        
        Returns:
            Cancelled command
        """
        command = await self.get_command_by_id(command_id)
        
        if not command.is_pending():
            raise ValidationException(
                detail=f"Command {command_id} cannot be cancelled. Current status: {command.status}"
            )
        
        command.status = "cancelled"
        command.completed_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(command)
        
        logger.info(
            f"Command cancelled: {command.command_type}",
            extra={
                "command_id": command.id,
                "command_type": command.command_type
            }
        )
        
        return command
    
    async def get_command_stats(self) -> CommandStats:
        """
        Get command statistics
        
        Returns:
            Command statistics
        """
        # Total commands
        result = await self.db.execute(select(func.count()).select_from(Command))
        total = result.scalar()
        
        # Count by status
        result = await self.db.execute(
            select(Command.status, func.count())
            .group_by(Command.status)
        )
        status_counts = dict(result.all())
        
        # Count by type
        result = await self.db.execute(
            select(Command.command_type, func.count())
            .group_by(Command.command_type)
        )
        type_counts = {str(k): v for k, v in result.all()}
        
        # Count by junction
        result = await self.db.execute(
            select(Command.junction_id, func.count())
            .where(Command.junction_id.isnot(None))
            .group_by(Command.junction_id)
        )
        junction_counts = {k: v for k, v in result.all()}
        
        # Average execution time (for completed commands)
        result = await self.db.execute(
            select(func.avg(
                func.extract('epoch', Command.completed_at) - 
                func.extract('epoch', Command.executed_at)
            ))
            .where(
                Command.executed_at.isnot(None),
                Command.completed_at.isnot(None)
            )
        )
        avg_time = result.scalar()
        
        return CommandStats(
            total_commands=total,
            pending_commands=status_counts.get("pending", 0),
            executing_commands=status_counts.get("executing", 0),
            success_commands=status_counts.get("success", 0),
            failed_commands=status_counts.get("failed", 0),
            timeout_commands=status_counts.get("timeout", 0),
            cancelled_commands=status_counts.get("cancelled", 0),
            commands_by_type=type_counts,
            commands_by_junction=junction_counts,
            average_execution_time=float(avg_time) if avg_time else None
        )
    
    async def get_pending_commands(self, limit: int = 100) -> List[Command]:
        """
        Get pending commands for execution
        
        Args:
            limit: Maximum number of commands to return
        
        Returns:
            List of pending commands
        """
        result = await self.db.execute(
            select(Command)
            .where(Command.status == "pending")
            .order_by(Command.created_at.asc())
            .limit(limit)
        )
        
        return list(result.scalars().all())
