"""
Application configuration management
"""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List
import secrets
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "ITMS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = Field("", env="DATABASE_URL")
    
    # JWT
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security
    BCRYPT_ROUNDS: int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Redis (optional)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Junction Communication
    JUNCTION_TIMEOUT_SECONDS: int = 10
    JUNCTION_RETRY_ATTEMPTS: int = 3
    JUNCTION_RETRY_BACKOFF: int = 2
    
    # VIP Mode
    VIP_MODE_DEFAULT_TIMEOUT_SECONDS: int = 300
    
    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # Control System (External Hardware/Simulation)
    CONTROL_SYSTEM_URL: str = "http://localhost:5000"
    CONTROL_SYSTEM_API_KEY: str = "dev-api-key"
    CONTROL_SYSTEM_TIMEOUT: int = 10
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v

    @validator("DATABASE_URL", pre=True)
    def normalize_database_url(cls, v):
        v = v or os.getenv("DATABASE_PRIVATE_URL") or os.getenv("DATABASE_PUBLIC_URL")
        if not v:
            raise ValueError("DATABASE_URL is required. Add a PostgreSQL database to Railway and reference its DATABASE_URL in this service.")
        if isinstance(v, str) and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
