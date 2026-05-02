"""
Junction schemas - Pydantic models for junction management
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import ipaddress


class JunctionStatusEnum:
    """Junction status constants"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    
    @classmethod
    def all_statuses(cls) -> list[str]:
        """Get all valid statuses"""
        return [cls.ONLINE, cls.OFFLINE, cls.MAINTENANCE, cls.ERROR]
    
    @classmethod
    def is_valid(cls, status: str) -> bool:
        """Check if status is valid"""
        return status in cls.all_statuses()


# Base schema with common fields
class JunctionBase(BaseModel):
    """Base junction schema"""
    name: str = Field(..., min_length=2, max_length=100, description="Junction name")
    location: Optional[str] = Field(None, max_length=255, description="Physical location")
    ip_address: str = Field(..., description="IP address of the controlling device")
    device_id: Optional[str] = Field(None, max_length=100, description="Unique device identifier")
    description: Optional[str] = Field(None, description="Additional description")
    zone: Optional[str] = Field(None, max_length=50, description="Zone or area classification")
    config_metadata: Optional[str] = Field(None, description="JSON configuration")
    
    @field_validator('ip_address')
    @classmethod
    def validate_ip_address(cls, v: str) -> str:
        """Validate IP address format"""
        try:
            # Try to parse as IPv4 or IPv6
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid IP address: {v}")


# Create junction request
class JunctionCreate(JunctionBase):
    """Schema for creating a new junction"""
    pass


# Update junction request
class JunctionUpdate(BaseModel):
    """Schema for updating a junction"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    ip_address: Optional[str] = Field(None)
    device_id: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, description="Junction status")
    description: Optional[str] = Field(None)
    zone: Optional[str] = Field(None, max_length=50)
    config_metadata: Optional[str] = Field(None)
    
    @field_validator('ip_address')
    @classmethod
    def validate_ip_address(cls, v: Optional[str]) -> Optional[str]:
        """Validate IP address format"""
        if v is None:
            return v
        try:
            ipaddress.ip_address(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid IP address: {v}")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate status"""
        if v is None:
            return v
        if not JunctionStatusEnum.is_valid(v):
            raise ValueError(
                f"Invalid status: {v}. Must be one of: {', '.join(JunctionStatusEnum.all_statuses())}"
            )
        return v


# Junction response
class JunctionResponse(JunctionBase):
    """Schema for junction response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# Junction list response with pagination
class JunctionListResponse(BaseModel):
    """Schema for paginated junction list"""
    junctions: list[JunctionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Junction status update
class JunctionStatusUpdate(BaseModel):
    """Schema for updating junction status"""
    status: str = Field(..., description="New junction status")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status"""
        if not JunctionStatusEnum.is_valid(v):
            raise ValueError(
                f"Invalid status: {v}. Must be one of: {', '.join(JunctionStatusEnum.all_statuses())}"
            )
        return v


# Heartbeat request (for device to report status)
class JunctionHeartbeat(BaseModel):
    """Schema for junction heartbeat"""
    device_id: str = Field(..., description="Device identifier")
    status: str = Field(default=JunctionStatusEnum.ONLINE, description="Current status")
    metadata: Optional[dict] = Field(None, description="Additional device metadata")


# Junction statistics
class JunctionStats(BaseModel):
    """Schema for junction statistics"""
    total_junctions: int
    online_junctions: int
    offline_junctions: int
    maintenance_junctions: int
    error_junctions: int
    junctions_by_zone: dict[str, int]
