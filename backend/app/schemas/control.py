"""
Control schemas - Request/response schemas for control endpoints
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Dict, Any, List


class SwitchModeRequest(BaseModel):
    """Switch mode request schema"""
    mode: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Mode to switch to (manual, auto_circle, auto_jump, blinker, vip)"
    )
    
    @field_validator('mode')
    @classmethod
    def validate_mode(cls, v: str) -> str:
        valid_modes = ['manual', 'auto_circle', 'auto_jump', 'blinker', 'vip']
        if v not in valid_modes:
            raise ValueError(f"Invalid mode. Must be one of: {', '.join(valid_modes)}")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "mode": "auto_circle"
            }
        }
    )


class SwitchModeResponse(BaseModel):
    """Switch mode response schema"""
    success: bool
    message: str
    previous_mode: str
    current_mode: str
    control_data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Mode switched successfully",
                "previous_mode": "manual",
                "current_mode": "auto_circle",
                "control_data": {"status": "ok"},
                "error": None
            }
        }
    )


class SetManualTimesRequest(BaseModel):
    """Set manual times request schema"""
    lane1: int = Field(..., ge=5, le=300, description="Lane 1 green time in seconds")
    lane2: int = Field(..., ge=5, le=300, description="Lane 2 green time in seconds")
    lane3: int = Field(..., ge=5, le=300, description="Lane 3 green time in seconds")
    lane4: int = Field(..., ge=5, le=300, description="Lane 4 green time in seconds")
    
    @field_validator('lane1', 'lane2', 'lane3', 'lane4')
    @classmethod
    def validate_timing(cls, v: int) -> int:
        if v < 5:
            raise ValueError("Minimum green time is 5 seconds")
        if v > 300:
            raise ValueError("Maximum green time is 300 seconds (5 minutes)")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "lane1": 30,
                "lane2": 45,
                "lane3": 30,
                "lane4": 45
            }
        }
    )


class SetManualTimesResponse(BaseModel):
    """Set manual times response schema"""
    success: bool
    message: str
    lane1: int
    lane2: int
    lane3: int
    lane4: int
    control_data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Manual times set successfully",
                "lane1": 30,
                "lane2": 45,
                "lane3": 30,
                "lane4": 45,
                "control_data": {"status": "ok"},
                "error": None
            }
        }
    )


class VIPOverrideRequest(BaseModel):
    """VIP override request schema"""
    active: bool = Field(..., description="True to activate VIP mode, False to deactivate")
    lanes_to_green: Optional[List[int]] = Field(
        None,
        description="List of lane numbers to turn green (1-4)"
    )
    
    @field_validator('lanes_to_green')
    @classmethod
    def validate_lanes(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None:
            for lane in v:
                if lane < 1 or lane > 4:
                    raise ValueError("Lane numbers must be between 1 and 4")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "active": True,
                "lanes_to_green": [2]
            }
        }
    )


class VIPOverrideResponse(BaseModel):
    """VIP override response schema"""
    success: bool
    message: str
    active: bool
    lanes_to_green: Optional[List[int]] = None
    control_data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "VIP mode activated",
                "active": True,
                "lanes_to_green": [2],
                "control_data": {"status": "ok"},
                "error": None
            }
        }
    )


class ControlStatusResponse(BaseModel):
    """Control status response schema"""
    success: bool
    message: str
    status_data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Status retrieved successfully",
                "status_data": {
                    "mode": "auto_circle",
                    "lane1": 30,
                    "lane2": 45,
                    "lane3": 30,
                    "lane4": 45,
                    "vip_active": False
                },
                "error": None
            }
        }
    )


class HealthCheckResponse(BaseModel):
    """Health check response schema"""
    healthy: bool
    message: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "healthy": True,
                "message": "Control system is healthy"
            }
        }
    )
