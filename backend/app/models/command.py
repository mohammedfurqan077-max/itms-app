"""
Command models - Command execution tracking for junction communication
"""
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.db.base import Base


# Command type constants (no longer ENUM)
class CommandType:
    """Command type constants"""
    SET_MODE = "set_mode"
    SET_TIME = "set_time"
    VIP_MODE = "vip_mode"
    EMERGENCY_STOP = "emergency_stop"
    HEARTBEAT = "heartbeat"
    GET_STATUS = "get_status"


# Command status constants (no longer ENUM)
class CommandStatus:
    """Command status constants"""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class Command(Base):
    """
    Command model - Tracks commands sent to junction devices
    
    This model provides a complete audit trail of all commands sent to
    junction devices, including their status, payload, and response.
    """
    __tablename__ = "commands"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Junction reference
    junction_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("junctions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Junction that received the command (null for broadcast commands)"
    )
    
    # Command details
    command_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of command being executed"
    )
    
    payload: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON payload containing command parameters"
    )
    
    # Status tracking
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
        comment="Current status of the command"
    )
    
    response: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON response from the junction device"
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if command failed"
    )
    
    # User tracking
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who initiated the command"
    )
    
    # Retry tracking
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of retry attempts"
    )
    
    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
        comment="Maximum number of retry attempts"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True,
        comment="When the command was created"
    )
    
    executed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="When the command was executed"
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="When the command completed (success or failure)"
    )
    
    # Relationships
    junction: Mapped[Optional["Junction"]] = relationship(
        "Junction",
        foreign_keys=[junction_id],
        lazy="joined"
    )
    
    user: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[created_by],
        lazy="joined"
    )

    # Indexes for common queries
    __table_args__ = (
        Index('idx_command_junction_status', 'junction_id', 'status'),
        Index('idx_command_type_status', 'command_type', 'status'),
        Index('idx_command_created_at', 'created_at'),
    )

    def __repr__(self) -> str:
        return f"<Command(id={self.id}, type={self.command_type}, status={self.status})>"
    
    def is_pending(self) -> bool:
        """Check if command is pending"""
        return self.status == "pending"
    
    def is_executing(self) -> bool:
        """Check if command is executing"""
        return self.status == "executing"
    
    def is_completed(self) -> bool:
        """Check if command is completed (success or failed)"""
        return self.status in ["success", "failed", "timeout", "cancelled"]
    
    def is_success(self) -> bool:
        """Check if command succeeded"""
        return self.status == "success"
    
    def is_failed(self) -> bool:
        """Check if command failed"""
        return self.status in ["failed", "timeout"]
    
    def can_retry(self) -> bool:
        """Check if command can be retried"""
        return self.is_failed() and self.retry_count < self.max_retries
