"""
Junction models - Traffic junction management
"""
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
import enum

from app.db.base import Base


class JunctionStatus(str, enum.Enum):
    """Junction status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class Junction(Base):
    """
    Junction model - Represents a traffic junction controlled by a device
    
    Each junction is controlled by a Raspberry Pi or similar device.
    The system tracks junction status, location, and device information.
    """
    __tablename__ = "junctions"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Basic information
    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        unique=True,
        index=True,
        comment="Junction name (must be unique)"
    )
    
    location: Mapped[Optional[str]] = mapped_column(
        String(255), 
        nullable=True,
        comment="Physical location or address of the junction"
    )
    
    # Device information
    ip_address: Mapped[str] = mapped_column(
        String(45),  # IPv6 support
        nullable=False,
        unique=True,
        index=True,
        comment="IP address of the controlling device"
    )
    
    device_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
        comment="Unique device identifier (e.g., Raspberry Pi serial number)"
    )
    
    # Status tracking
    status: Mapped[JunctionStatus] = mapped_column(
        SQLEnum(JunctionStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=JunctionStatus.OFFLINE,
        index=True,
        comment="Current junction status"
    )
    
    last_seen: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Last time the junction device sent a heartbeat"
    )
    
    # Additional metadata
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional description or notes about the junction"
    )
    
    zone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="Zone or area classification (e.g., 'Zone A', 'Downtown')"
    )
    
    # Configuration
    config_metadata: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON configuration for junction-specific settings"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="Junction creation timestamp"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        comment="Last update timestamp"
    )

    # Indexes for common queries
    __table_args__ = (
        Index('idx_junction_status_zone', 'status', 'zone'),
        Index('idx_junction_last_seen', 'last_seen'),
    )

    def __repr__(self) -> str:
        return f"<Junction(id={self.id}, name={self.name}, status={self.status})>"
    
    def is_online(self) -> bool:
        """Check if junction is currently online"""
        return self.status == JunctionStatus.ONLINE
    
    def is_offline(self) -> bool:
        """Check if junction is currently offline"""
        return self.status == JunctionStatus.OFFLINE
