"""
Command Executor Service - Background processor for pending commands

This service runs as a background task and automatically processes pending commands
from the database using the control service.
"""
import asyncio
from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.models.command import Command
from app.services.control_service import ControlService, get_control_service
from app.db.session import AsyncSessionLocal
from app.core.logging import logger
from app.core.exceptions import ValidationException


class CommandExecutor:
    """
    Background command executor
    
    Continuously polls the database for pending commands and executes them
    using the control service.
    """
    
    def __init__(
        self,
        poll_interval: int = 2,
        control_service: Optional[ControlService] = None
    ):
        """
        Initialize command executor
        
        Args:
            poll_interval: Seconds between database polls (default: 2)
            control_service: Control service instance (default: singleton)
        """
        self.poll_interval = poll_interval
        self.control_service = control_service or get_control_service()
        self.running = False
        self._task: Optional[asyncio.Task] = None
        
        logger.info(
            "CommandExecutor initialized",
            extra={"poll_interval": poll_interval}
        )
    
    async def start(self):
        """Start the background executor"""
        if self.running:
            logger.warning("CommandExecutor already running")
            return
        
        self.running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("CommandExecutor started")
    
    async def stop(self):
        """Stop the background executor"""
        if not self.running:
            return
        
        self.running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("CommandExecutor stopped")
    
    async def _run_loop(self):
        """Main execution loop"""
        logger.info("CommandExecutor loop started")
        
        while self.running:
            try:
                await self._process_pending_commands()
            except Exception as e:
                logger.error(
                    "Error in command executor loop",
                    extra={"error": str(e)},
                    exc_info=True
                )
            
            # Wait before next poll
            await asyncio.sleep(self.poll_interval)
        
        logger.info("CommandExecutor loop stopped")
    
    async def _process_pending_commands(self):
        """Process all pending commands"""
        # Create new database session for this iteration
        async with AsyncSessionLocal() as db:
            try:
                # Fetch pending commands
                result = await db.execute(
                    select(Command)
                    .where(Command.status == "pending")
                    .order_by(Command.created_at.asc())
                    .limit(100)  # Process up to 100 commands per iteration
                )
                
                commands = result.scalars().all()
                
                if commands:
                    logger.info(
                        f"Found {len(commands)} pending command(s) to process"
                    )
                
                # Process each command
                for command in commands:
                    try:
                        await self._execute_command(db, command)
                    except Exception as e:
                        logger.error(
                            f"Failed to execute command {command.id}",
                            extra={
                                "command_id": command.id,
                                "command_type": command.command_type,
                                "error": str(e)
                            },
                            exc_info=True
                        )
            
            except Exception as e:
                logger.error(
                    "Error fetching pending commands",
                    extra={"error": str(e)},
                    exc_info=True
                )
    
    async def _execute_command(self, db: AsyncSession, command: Command):
        """
        Execute a single command
        
        Args:
            db: Database session
            command: Command to execute
        """
        logger.info(
            f"Picked command for execution: {command.command_type}",
            extra={
                "command_id": command.id,
                "command_type": command.command_type,
                "junction_id": command.junction_id,
                "created_at": command.created_at.isoformat()
            }
        )
        
        # Update status to EXECUTING
        command.status = "executing"
        command.executed_at = datetime.utcnow()
        await db.commit()
        
        logger.info(
            f"Started executing command: {command.command_type}",
            extra={
                "command_id": command.id,
                "command_type": command.command_type
            }
        )
        
        try:
            # Parse payload
            payload = {}
            if command.payload:
                try:
                    payload = json.loads(command.payload)
                except json.JSONDecodeError as e:
                    raise ValidationException(
                        detail=f"Invalid JSON payload: {str(e)}"
                    )
            
            # Execute based on command type
            response = None
            
            if command.command_type == "set_mode":
                # Switch mode
                mode = payload.get('mode')
                if not mode:
                    raise ValidationException(
                        detail="'mode' is required in payload for SET_MODE command"
                    )
                
                response = await self.control_service.switch_mode(mode)
            
            elif command.command_type == "set_time":
                # Set manual times
                lane1 = payload.get('lane1')
                lane2 = payload.get('lane2')
                lane3 = payload.get('lane3')
                lane4 = payload.get('lane4')
                
                if not all([lane1 is not None, lane2 is not None, 
                           lane3 is not None, lane4 is not None]):
                    raise ValidationException(
                        detail="All lane times (lane1, lane2, lane3, lane4) are required for SET_TIME command"
                    )
                
                response = await self.control_service.set_manual_times(
                    lane1=int(lane1),
                    lane2=int(lane2),
                    lane3=int(lane3),
                    lane4=int(lane4)
                )
            
            elif command.command_type == "vip_mode":
                # VIP override
                active = payload.get('active', False)
                lanes_to_green = payload.get('lanes_to_green')
                
                response = await self.control_service.vip_override(
                    active=bool(active),
                    lanes_to_green=lanes_to_green
                )
            
            elif command.command_type == "get_status":
                # Get status
                response = await self.control_service.get_status()
            
            elif command.command_type == "emergency_stop":
                # Emergency stop
                response = await self.control_service.emergency_stop()
            
            elif command.command_type == "heartbeat":
                # Heartbeat (same as get_status)
                response = await self.control_service.get_status()
            
            else:
                raise ValidationException(
                    detail=f"Unsupported command type: {command.command_type}"
                )
            
            # Check if execution was successful
            if response and response.success:
                # Success
                command.status = "success"
                command.response = json.dumps(response.to_dict())
                command.error_message = None
                command.completed_at = datetime.utcnow()
                
                logger.info(
                    f"Command completed successfully: {command.command_type}",
                    extra={
                        "command_id": command.id,
                        "command_type": command.command_type,
                        "response": response.to_dict()
                    }
                )
            else:
                # Failed
                error_msg = response.error if response else "Unknown error"
                command.status = "failed"
                command.error_message = error_msg
                command.response = json.dumps(response.to_dict()) if response else None
                command.completed_at = datetime.utcnow()
                
                logger.error(
                    f"Command failed: {command.command_type}",
                    extra={
                        "command_id": command.id,
                        "command_type": command.command_type,
                        "error": error_msg
                    }
                )
        
        except ValidationException as e:
            # Validation error
            command.status = "failed"
            command.error_message = str(e)
            command.completed_at = datetime.utcnow()
            
            logger.error(
                f"Command validation failed: {command.command_type}",
                extra={
                    "command_id": command.id,
                    "command_type": command.command_type,
                    "error": str(e)
                }
            )
        
        except Exception as e:
            # Unexpected error
            error_msg = str(e)
            command.status = "failed"
            command.error_message = error_msg
            command.completed_at = datetime.utcnow()
            
            logger.error(
                f"Command execution failed: {command.command_type}",
                extra={
                    "command_id": command.id,
                    "command_type": command.command_type,
                    "error": error_msg
                },
                exc_info=True
            )
        
        # Commit changes
        await db.commit()
        await db.refresh(command)


# Global executor instance
_executor_instance: Optional[CommandExecutor] = None


def get_command_executor() -> CommandExecutor:
    """
    Get singleton instance of CommandExecutor
    
    Returns:
        CommandExecutor: Singleton instance
    """
    global _executor_instance
    
    if _executor_instance is None:
        _executor_instance = CommandExecutor()
    
    return _executor_instance


def reset_command_executor():
    """Reset singleton instance (useful for testing)"""
    global _executor_instance
    _executor_instance = None
