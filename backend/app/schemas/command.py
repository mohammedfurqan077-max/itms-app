"""
Command schemas - Pydantic models for command execution
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Any
from datetime import datetime
import json


class CommandTypeEnum:
    """Command type constants"""
    SET_MODE = "set_mode"
    SET_TIME = "set_time"
    VIP_MODE = "vip_mode"
    EMERGENCY_STOP = "emergency_stop"
    HEARTBEAT = "heartbeat"
    GET_STATUS = "get_status"
    
    @classmethod
    def all_types(cls) -> list[str]:
        """Get all valid command types"""
        return [
            cls.SET_MODE,
            cls.SET_TIME,
            cls.VIP_MODE,
            cls.EMERGENCY_STOP,
            cls.HEARTBEAT,
            cls.GET_STATUS
        ]
    
    @classmethod
    def is_valid(cls, command_type: str) -> bool:
        """Check if command type is valid"""
        return command_type in cls.all_types()


class CommandStatusEnum:
    """Command status constants"""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    
    @classmethod
    def all_statuses(cls) -> list[str]:
        """Get all valid statuses"""
        return [
            cls.PENDING,
            cls.EXECUTING,
            cls.SUCCESS,
            cls.FAILED,
            cls.TIMEOUT,
            cls.CANCELLED
        ]
    
    @classmethod
    def is_valid(cls, status: str) -> bool:
        """Check if status is valid"""
        return status in cls.all_statuses()


# Base schema
class CommandBase(BaseModel):
    """Base command schema"""
    junction_id: Optional[int] = Field(None, description="Junction ID (null for broadcast)")
    command_type: str = Field(..., description="Type of command")
    payload: Optional[dict] = Field(None, description="Command parameters")
    
    @field_validator('command_type')
    @classmethod
    def validate_command_type(cls, v: str) -> str:
        """Validate command type"""
        if not CommandTypeEnum.is_valid(v):
            raise ValueError(
                f"Invalid command type: {v}. Must be one of: {', '.join(CommandTypeEnum.all_types())}"
            )
        return v


# Create command request
class CommandCreate(CommandBase):
    """Schema for creating a new command"""
    max_retries: Optional[int] = Field(3, ge=0, le=10, description="Maximum retry attempts")


# Send command request (simplified)
class SendCommandRequest(BaseModel):
    """Schema for sending a command"""
    junction_id: Optional[int] = Field(None, description="Junction ID (null for broadcast)")
    command_type: str = Field(..., description="Type of command")
    payload: Optional[dict] = Field(None, description="Command parameters")
    execute_immediately: bool = Field(True, description="Execute immediately or queue")
    
    @field_validator('command_type')
    @classmethod
    def validate_command_type(cls, v: str) -> str:
        """Validate command type"""
        if not CommandTypeEnum.is_valid(v):
            raise ValueError(
                f"Invalid command type: {v}. Must be one of: {', '.join(CommandTypeEnum.all_types())}"
            )
        return v


# Command response
class CommandResponse(BaseModel):
    """Schema for command response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    junction_id: Optional[int] = None
    command_type: str
    payload: Optional[str] = None
    status: str
    response: Optional[str] = None
    error_message: Optional[str] = None
    created_by: Optional[int] = None
    retry_count: int
    max_retries: int
    created_at: datetime
    executed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Computed fields
    @property
    def payload_dict(self) -> Optional[dict]:
        """Parse payload JSON to dict"""
        if self.payload:
            try:
                return json.loads(self.payload)
            except:
                return None
        return None
    
    @property
    def response_dict(self) -> Optional[dict]:
        """Parse response JSON to dict"""
        if self.response:
            try:
                return json.loads(self.response)
            except:
                return None
        return None


# Command list response with pagination
class CommandListResponse(BaseModel):
    """Schema for paginated command list"""
    commands: list[CommandResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Command execution result
class CommandExecutionResult(BaseModel):
    """Schema for command execution result"""
    command_id: int
    success: bool
    message: str
    status: str
    response_data: Optional[dict] = None
    error: Optional[str] = None
    executed_at: Optional[datetime] = None


# Command statistics
class CommandStats(BaseModel):
    """Schema for command statistics"""
    total_commands: int
    pending_commands: int
    executing_commands: int
    success_commands: int
    failed_commands: int
    timeout_commands: int
    cancelled_commands: int
    commands_by_type: dict[str, int]
    commands_by_junction: dict[int, int]
    average_execution_time: Optional[float] = None


# Retry command request
class RetryCommandRequest(BaseModel):
    """Schema for retrying a failed command"""
    force: bool = Field(False, description="Force retry even if max retries reached")
