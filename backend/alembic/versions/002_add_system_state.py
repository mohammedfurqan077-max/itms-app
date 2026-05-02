"""Add system_state table

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create junctions table (minimal for now)
    op.create_table(
        'junctions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_junctions_id'), 'junctions', ['id'], unique=False)

    # Create system_state table (singleton)
    op.create_table(
        'system_state',
        sa.Column('id', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('current_mode', sa.String(length=50), nullable=False, server_default='manual'),
        sa.Column('last_updated_by', sa.Integer(), nullable=True),
        sa.Column('junction_id', sa.Integer(), nullable=True),
        sa.Column('mode_metadata', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['last_updated_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['junction_id'], ['junctions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_system_state_id'), 'system_state', ['id'], unique=False)
    
    # Add check constraint to ensure only one row (singleton pattern)
    op.create_check_constraint(
        'singleton_check',
        'system_state',
        'id = 1'
    )
    
    # Insert default system state
    op.execute("""
        INSERT INTO system_state (id, current_mode, last_updated_by, junction_id, mode_metadata)
        VALUES (1, 'manual', NULL, NULL, NULL)
    """)


def downgrade() -> None:
    op.drop_index(op.f('ix_system_state_id'), table_name='system_state')
    op.drop_table('system_state')
    
    op.drop_index(op.f('ix_junctions_id'), table_name='junctions')
    op.drop_table('junctions')
