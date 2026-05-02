"""
SystemState schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class SystemStateResponse(BaseModel):
    """System state response schema"""
    id: int
    current_mode: str
    last_updated_by: Optional[int] = None
    junction_id: Optional[int] = None
    mode_metadata: Optional[str] = None
    updated_at: datetime
    created_at: datetime
    
    # Nested user info (if available)
    updated_by_name: Optional[str] = None
    junction_name: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "current_mode": "manual",
                "last_updated_by": 1,
                "junction_id": None,
                "mode_metadata": None,
                "updated_at": "2024-01-15T10:30:00",
                "created_at": "2024-01-01T00:00:00",
                "updated_by_name": "Admin User",
                "junction_name": None
            }
        }
    )


class UpdateSystemStateRequest(BaseModel):
    """Update system state request schema"""
    new_mode: str = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="New system mode (manual, auto_circle, auto_jump, blinker, vip)"
    )
    junction_id: Optional[int] = Field(
        None,
        description="Junction ID for junction-specific modes (e.g., VIP mode)"
    )
    mode_metadata: Optional[str] = Field(
        None,
        description="JSON metadata for mode-specific configuration"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "new_mode": "auto_circle",
                "junction_id": None,
                "mode_metadata": None
            }
        }
    )


class UpdateSystemStateResponse(BaseModel):
    """Update system state response schema"""
    success: bool
    message: str
    previous_mode: str
    current_mode: str
    system_state: SystemStateResponse

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "System mode updated successfully",
                "previous_mode": "manual",
                "current_mode": "auto_circle",
                "system_state": {
                    "id": 1,
                    "current_mode": "auto_circle",
                    "last_updated_by": 1,
                    "junction_id": None,
                    "mode_metadata": None,
                    "updated_at": "2024-01-15T10:30:00",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_by_name": "Admin User",
                    "junction_name": None
                }
            }
        }
    )


class SystemModeEnum:
    """Valid system modes"""
    MANUAL = "manual"
    AUTO_CIRCLE = "auto_circle"
    AUTO_JUMP = "auto_jump"
    BLINKER = "blinker"
    VIP = "vip"
    
    @classmethod
    def all_modes(cls) -> list[str]:
        """Get all valid modes"""
        return [cls.MANUAL, cls.AUTO_CIRCLE, cls.AUTO_JUMP, cls.BLINKER, cls.VIP]
    
    @classmethod
    def is_valid(cls, mode: str) -> bool:
        """Check if mode is valid"""
        return mode in cls.all_modes()
