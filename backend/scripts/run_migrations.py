"""Run database migrations with a non-destructive schema fallback."""

import asyncio
import sys

from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine, AsyncSessionLocal
from app.models import Command, Junction, Permission, SystemState, User  # noqa: F401
from alembic import command
from alembic.config import Config


PERMISSIONS = [
    ("set_time", "Set manual signal timings"),
    ("auto_jump", "Use auto jump mode"),
    ("auto_circle", "Use auto circle mode"),
    ("blinker", "Use yellow blinker mode"),
    ("vip_mode", "Activate VIP mode for emergency vehicles"),
]

SAMPLE_JUNCTIONS = [
    {
        "name": "Main Square Junction",
        "location": "Main Square, Downtown",
        "ip_address": "192.168.1.100",
        "device_id": "RPI-001",
        "status": "offline",
        "description": "Primary junction at main square",
        "zone": "Zone A",
    },
    {
        "name": "North Gate Junction",
        "location": "North Gate Entrance",
        "ip_address": "192.168.1.101",
        "device_id": "RPI-002",
        "status": "offline",
        "description": "Junction at north gate",
        "zone": "Zone B",
    },
    {
        "name": "South Plaza Junction",
        "location": "South Plaza",
        "ip_address": "192.168.1.102",
        "device_id": "RPI-003",
        "status": "offline",
        "description": "Junction at south plaza",
        "zone": "Zone A",
    },
]


async def create_schema_from_models() -> None:
    """Create missing tables and seed required defaults without dropping data."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await repair_partial_schema(connection)

    async with AsyncSessionLocal() as session:
        for name, description in PERMISSIONS:
            await session.execute(
                text(
                    """
                    INSERT INTO permissions (name, description)
                    VALUES (:name, :description)
                    ON CONFLICT (name) DO NOTHING
                    """
                ),
                {"name": name, "description": description},
            )

        await session.execute(
            text(
                """
                INSERT INTO system_state (id, current_mode)
                VALUES (1, 'manual')
                ON CONFLICT (id) DO NOTHING
                """
            )
        )
        for junction in SAMPLE_JUNCTIONS:
            await session.execute(
                text(
                    """
                    INSERT INTO junctions (
                        name, location, ip_address, device_id, status, description, zone
                    )
                    VALUES (
                        :name, :location, :ip_address, :device_id, :status, :description, :zone
                    )
                    ON CONFLICT (name) DO NOTHING
                    """
                ),
                junction,
            )

        await session.commit()

    await engine.dispose()


async def repair_partial_schema(connection) -> None:
    """Repair tables that may have been created by an earlier partial migration."""
    statements = [
        "ALTER TABLE junctions ADD COLUMN IF NOT EXISTS location VARCHAR(255)",
        "ALTER TABLE junctions ADD COLUMN IF NOT EXISTS device_id VARCHAR(100)",
        "ALTER TABLE junctions ADD COLUMN IF NOT EXISTS status VARCHAR(50) NOT NULL DEFAULT 'offline'",
        "ALTER TABLE junctions ADD COLUMN IF NOT EXISTS last_seen TIMESTAMP",
        "ALTER TABLE junctions ADD COLUMN IF NOT EXISTS description TEXT",
        "ALTER TABLE junctions ADD COLUMN IF NOT EXISTS zone VARCHAR(50)",
        "ALTER TABLE junctions ADD COLUMN IF NOT EXISTS config_metadata TEXT",
        "ALTER TABLE junctions ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP NOT NULL DEFAULT NOW()",
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_junctions_name ON junctions (name)",
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_junctions_ip_address ON junctions (ip_address)",
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_junctions_device_id ON junctions (device_id)",
        "CREATE INDEX IF NOT EXISTS ix_junctions_status ON junctions (status)",
        "CREATE INDEX IF NOT EXISTS ix_junctions_zone ON junctions (zone)",
        "CREATE INDEX IF NOT EXISTS idx_junction_status_zone ON junctions (status, zone)",
        "CREATE INDEX IF NOT EXISTS idx_junction_last_seen ON junctions (last_seen)",
    ]
    for statement in statements:
        await connection.execute(text(statement))


def stamp_head() -> None:
    alembic_cfg = Config("alembic.ini")
    command.stamp(alembic_cfg, "head")


def main() -> None:
    alembic_cfg = Config("alembic.ini")
    try:
        command.upgrade(alembic_cfg, "head")
        return
    except Exception as error:
        print(f"Alembic migration failed: {error}", file=sys.stderr)
        print("Creating any missing tables from SQLAlchemy models instead.", file=sys.stderr)

    asyncio.run(create_schema_from_models())
    stamp_head()


if __name__ == "__main__":
    main()
