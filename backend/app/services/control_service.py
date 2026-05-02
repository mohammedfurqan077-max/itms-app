"""
Control service - Communication with external control system
This service handles all communication with the traffic control hardware/simulation layer.
"""
from typing import Optional, Dict, Any, List
import httpx
from datetime import datetime

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import JunctionException


class ControlServiceResponse:
    """Structured response from control service"""
    
    def __init__(
        self,
        success: bool,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        status_code: Optional[int] = None
    ):
        self.success = success
        self.message = message
        self.data = data or {}
        self.error = error
        self.status_code = status_code
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "status_code": self.status_code,
            "timestamp": self.timestamp.isoformat()
        }


class ControlService:
    """
    Control service for external control system communication
    
    This service communicates with the traffic control hardware/simulation layer.
    Currently connects to a simulation server, but designed to be easily replaced
    with Raspberry Pi communication in the future.
    
    Base URL: http://localhost:5000 (configurable)
    Authentication: X-API-KEY header
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 10
    ):
        """
        Initialize control service
        
        Args:
            base_url: Base URL of control system (default from settings)
            api_key: API key for authentication (default from settings)
            timeout: Request timeout in seconds (default: 10)
        """
        self.base_url = base_url or getattr(settings, 'CONTROL_SYSTEM_URL', 'http://localhost:5000')
        self.api_key = api_key or getattr(settings, 'CONTROL_SYSTEM_API_KEY', 'dev-api-key')
        self.timeout = timeout
        
        # Remove trailing slash from base URL
        self.base_url = self.base_url.rstrip('/')
        
        logger.info(f"ControlService initialized with base_url: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with API key"""
        return {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "ITMS-Backend/1.0"
        }
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> ControlServiceResponse:
        """
        Make HTTP request to control system
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., '/switch_mode')
            data: Request body data
            params: Query parameters
        
        Returns:
            ControlServiceResponse: Structured response
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.debug(
                    f"Control request: {method} {url}",
                    extra={"data": data, "params": params}
                )
                
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self._get_headers(),
                    json=data,
                    params=params
                )
                
                # Parse response
                try:
                    response_data = response.json()
                except Exception:
                    response_data = {"raw": response.text}
                
                # Check if request was successful
                if response.is_success:
                    logger.info(
                        f"Control request successful: {method} {endpoint}",
                        extra={"status_code": response.status_code}
                    )
                    return ControlServiceResponse(
                        success=True,
                        message="Request successful",
                        data=response_data,
                        status_code=response.status_code
                    )
                else:
                    logger.warning(
                        f"Control request failed: {method} {endpoint}",
                        extra={
                            "status_code": response.status_code,
                            "response": response_data
                        }
                    )
                    return ControlServiceResponse(
                        success=False,
                        message=f"Request failed with status {response.status_code}",
                        data=response_data,
                        error=response_data.get("error", "Unknown error"),
                        status_code=response.status_code
                    )
        
        except httpx.TimeoutException as e:
            logger.error(f"Control request timeout: {endpoint}", exc_info=True)
            return ControlServiceResponse(
                success=False,
                message="Request timeout",
                error=f"Connection timeout after {self.timeout} seconds"
            )
        
        except httpx.ConnectError as e:
            logger.error(f"Control connection error: {endpoint}", exc_info=True)
            return ControlServiceResponse(
                success=False,
                message="Connection error",
                error=f"Failed to connect to control system at {self.base_url}"
            )
        
        except httpx.HTTPError as e:
            logger.error(f"Control HTTP error: {endpoint}", exc_info=True)
            return ControlServiceResponse(
                success=False,
                message="HTTP error",
                error=str(e)
            )
        
        except Exception as e:
            logger.error(f"Control unexpected error: {endpoint}", exc_info=True)
            return ControlServiceResponse(
                success=False,
                message="Unexpected error",
                error=str(e)
            )
    
    async def switch_mode(self, mode_name: str) -> ControlServiceResponse:
        """
        Switch traffic control mode
        
        Args:
            mode_name: Mode to switch to (manual, auto_circle, auto_jump, blinker, vip)
        
        Returns:
            ControlServiceResponse: Response from control system
        
        Example:
            response = await control_service.switch_mode("auto_circle")
            if response.success:
                print("Mode switched successfully")
        """
        logger.info(f"Switching mode to: {mode_name}")
        
        return await self._make_request(
            method="POST",
            endpoint="/switch_mode",
            data={"mode": mode_name}
        )
    
    async def set_manual_times(
        self,
        lane1: int,
        lane2: int,
        lane3: int,
        lane4: int
    ) -> ControlServiceResponse:
        """
        Set manual timing for all lanes
        
        Args:
            lane1: Green time for lane 1 in seconds
            lane2: Green time for lane 2 in seconds
            lane3: Green time for lane 3 in seconds
            lane4: Green time for lane 4 in seconds
        
        Returns:
            ControlServiceResponse: Response from control system
        
        Example:
            response = await control_service.set_manual_times(30, 45, 30, 45)
            if response.success:
                print("Manual times set successfully")
        """
        logger.info(
            f"Setting manual times: L1={lane1}s, L2={lane2}s, L3={lane3}s, L4={lane4}s"
        )
        
        return await self._make_request(
            method="POST",
            endpoint="/set_manual_times",
            data={
                "lane1": lane1,
                "lane2": lane2,
                "lane3": lane3,
                "lane4": lane4
            }
        )
    
    async def vip_override(
        self,
        active: bool,
        lanes_to_green: Optional[List[int]] = None
    ) -> ControlServiceResponse:
        """
        Activate or deactivate VIP override mode
        
        Args:
            active: True to activate VIP mode, False to deactivate
            lanes_to_green: List of lane numbers to turn green (e.g., [1, 2])
        
        Returns:
            ControlServiceResponse: Response from control system
        
        Example:
            # Activate VIP mode for lane 2
            response = await control_service.vip_override(True, [2])
            
            # Deactivate VIP mode
            response = await control_service.vip_override(False)
        """
        logger.info(
            f"VIP override: active={active}, lanes={lanes_to_green}"
        )
        
        data = {"active": active}
        if lanes_to_green is not None:
            data["lanes_to_green"] = lanes_to_green
        
        return await self._make_request(
            method="POST",
            endpoint="/vip_override",
            data=data
        )
    
    async def get_status(self) -> ControlServiceResponse:
        """
        Get current status from control system
        
        Returns:
            ControlServiceResponse: Current status including mode, timings, etc.
        
        Example:
            response = await control_service.get_status()
            if response.success:
                current_mode = response.data.get("mode")
                print(f"Current mode: {current_mode}")
        """
        logger.debug("Getting control system status")
        
        return await self._make_request(
            method="GET",
            endpoint="/status"
        )
    
    async def health_check(self) -> bool:
        """
        Check if control system is reachable
        
        Returns:
            bool: True if control system is healthy, False otherwise
        
        Example:
            is_healthy = await control_service.health_check()
            if not is_healthy:
                print("Control system is not responding")
        """
        try:
            response = await self._make_request(
                method="GET",
                endpoint="/health"
            )
            return response.success
        except Exception:
            return False
    
    async def emergency_stop(self) -> ControlServiceResponse:
        """
        Emergency stop - set all signals to red/blinker
        
        Returns:
            ControlServiceResponse: Response from control system
        
        Example:
            response = await control_service.emergency_stop()
        """
        logger.warning("Emergency stop triggered")
        
        return await self._make_request(
            method="POST",
            endpoint="/emergency_stop",
            data={}
        )


# Singleton instance for easy access
_control_service_instance: Optional[ControlService] = None


def get_control_service() -> ControlService:
    """
    Get singleton instance of ControlService
    
    Returns:
        ControlService: Singleton instance
    
    Example:
        control_service = get_control_service()
        response = await control_service.switch_mode("auto_circle")
    """
    global _control_service_instance
    
    if _control_service_instance is None:
        _control_service_instance = ControlService()
    
    return _control_service_instance


def reset_control_service():
    """
    Reset singleton instance (useful for testing)
    """
    global _control_service_instance
    _control_service_instance = None
