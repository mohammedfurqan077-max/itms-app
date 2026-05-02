"""
SystemState model - Singleton pattern for global system state tracking
"""
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from app.db.base import Base


class SystemState(Base):
    """
    SystemState model - Singleton pattern
    
    Only one row exists in this table to track the current global system mode.
    This ensures a single source of truth for the system's operational state.
    """
    __tablename__ = "system_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    
    # Current system mode
    current_mode: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        default="manual",
        comment="Current traffic system mode (manual, auto_circle, auto_jump, blinker, vip)"
    )
    
    # Tracking information
    last_updated_by: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="SET NULL"), 
        nullable=True,
        comment="User who last updated the system state"
    )
    
    junction_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("junctions.id", ondelete="SET NULL"),
        nullable=True,
        comment="Junction ID if mode is junction-specific (e.g., VIP mode)"
    )
    
    # Additional context
    mode_metadata: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="JSON metadata for mode-specific configuration"
    )
    
    # Timestamps
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow, 
        nullable=False
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        nullable=False
    )

    # Relationships
    updated_by_user: Mapped[Optional["User"]] = relationship(
        "User", 
        foreign_keys=[last_updated_by],
        lazy="joined"
    )
    
    junction: Mapped[Optional["Junction"]] = relationship(
        "Junction",
        foreign_keys=[junction_id],
        lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<SystemState(id={self.id}, mode={self.current_mode}, updated_at={self.updated_at})>"
    
    @classmethod
    def get_singleton_id(cls) -> int:
        """Get the singleton ID (always 1)"""
        return 1
