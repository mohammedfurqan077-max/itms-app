"""
Main API router - aggregates all endpoint routers
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, system, control, junctions, commands

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(system.router, prefix="/system", tags=["System State"])
api_router.include_router(control.router, prefix="/control", tags=["Control System"])
api_router.include_router(junctions.router, prefix="/junctions", tags=["Junctions"])
api_router.include_router(commands.router, prefix="/commands", tags=["Commands"])

# To be added:
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(logs.router, prefix="/logs", tags=["Audit Logs"])
# api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
