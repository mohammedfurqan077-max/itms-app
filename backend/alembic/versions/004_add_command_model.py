"""Add command model for command execution tracking

Revision ID: 004
Revises: 003
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema"""

    op.create_table(
        'commands',
        sa.Column('id', sa.Integer(), primary_key=True),

        sa.Column('junction_id', sa.Integer(), nullable=True),

        # 🔥 USING STRING INSTEAD OF ENUM (FIXED)
        sa.Column('command_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),

        sa.Column('payload', sa.Text(), nullable=True),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),

        sa.Column('created_by', sa.Integer(), nullable=True),

        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_retries', sa.Integer(), nullable=False, server_default='3'),

        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['junction_id'], ['junctions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )

    # Indexes
    op.create_index('ix_commands_id', 'commands', ['id'])
    op.create_index('ix_commands_junction_id', 'commands', ['junction_id'])
    op.create_index('ix_commands_command_type', 'commands', ['command_type'])
    op.create_index('ix_commands_status', 'commands', ['status'])
    op.create_index('ix_commands_created_by', 'commands', ['created_by'])
    op.create_index('ix_commands_created_at', 'commands', ['created_at'])

    op.create_index('idx_command_junction_status', 'commands', ['junction_id', 'status'])
    op.create_index('idx_command_type_status', 'commands', ['command_type', 'status'])


def downgrade() -> None:
    """Downgrade database schema"""

    op.drop_table('commands')