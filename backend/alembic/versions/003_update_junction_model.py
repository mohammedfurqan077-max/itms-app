"""Update junction model with full fields

Revision ID: 003
Revises: 002
Create Date: 2026-04-30 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema"""
    
    # Drop the old junctions table if it exists (placeholder version)
    op.execute("DROP TABLE IF EXISTS junctions CASCADE")
    
    # Create junctions table with full schema
    op.create_table(
        'junctions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False, comment='Junction name (must be unique)'),
        sa.Column('location', sa.String(length=255), nullable=True, comment='Physical location or address of the junction'),
        sa.Column('ip_address', sa.String(length=45), nullable=False, comment='IP address of the controlling device'),
        sa.Column('device_id', sa.String(length=100), nullable=True, comment='Unique device identifier (e.g., Raspberry Pi serial number)'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='offline', comment='Current junction status'),
        sa.Column('last_seen', sa.DateTime(), nullable=True, comment='Last time the junction device sent a heartbeat'),
        sa.Column('description', sa.Text(), nullable=True, comment='Additional description or notes about the junction'),
        sa.Column('zone', sa.String(length=50), nullable=True, comment="Zone or area classification (e.g., 'Zone A', 'Downtown')"),
        sa.Column('config_metadata', sa.Text(), nullable=True, comment='JSON configuration for junction-specific settings'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='Junction creation timestamp'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), comment='Last update timestamp'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_junctions_id', 'junctions', ['id'], unique=False)
    op.create_index('ix_junctions_name', 'junctions', ['name'], unique=True)
    op.create_index('ix_junctions_ip_address', 'junctions', ['ip_address'], unique=True)
    op.create_index('ix_junctions_device_id', 'junctions', ['device_id'], unique=True)
    op.create_index('ix_junctions_status', 'junctions', ['status'], unique=False)
    op.create_index('ix_junctions_zone', 'junctions', ['zone'], unique=False)
    op.create_index('idx_junction_status_zone', 'junctions', ['status', 'zone'], unique=False)
    op.create_index('idx_junction_last_seen', 'junctions', ['last_seen'], unique=False)
    
    # Insert sample junctions for testing
    op.execute("""
        INSERT INTO junctions (name, location, ip_address, device_id, status, description, zone, created_at, updated_at)
        VALUES 
            ('Main Square Junction', 'Main Square, Downtown', '192.168.1.100', 'RPI-001', 'offline', 'Primary junction at main square', 'Zone A', NOW(), NOW()),
            ('North Gate Junction', 'North Gate Entrance', '192.168.1.101', 'RPI-002', 'offline', 'Junction at north gate', 'Zone B', NOW(), NOW()),
            ('South Plaza Junction', 'South Plaza', '192.168.1.102', 'RPI-003', 'offline', 'Junction at south plaza', 'Zone A', NOW(), NOW())
    """)


def downgrade() -> None:
    """Downgrade database schema"""
    
    # Drop indexes
    op.drop_index('idx_junction_last_seen', table_name='junctions')
    op.drop_index('idx_junction_status_zone', table_name='junctions')
    op.drop_index('ix_junctions_zone', table_name='junctions')
    op.drop_index('ix_junctions_status', table_name='junctions')
    op.drop_index('ix_junctions_device_id', table_name='junctions')
    op.drop_index('ix_junctions_ip_address', table_name='junctions')
    op.drop_index('ix_junctions_name', table_name='junctions')
    op.drop_index('ix_junctions_id', table_name='junctions')
    
    # Drop table
    op.drop_table('junctions')
    
    # Recreate placeholder junctions table
    op.create_table(
        'junctions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_junctions_id', 'junctions', ['id'], unique=False)
