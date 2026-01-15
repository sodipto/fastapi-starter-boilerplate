"""add_email_logger_table

Revision ID: a1b2c3d4e5f6
Revises: 31212482295b
Create Date: 2026-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '31212482295b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create email_logs table
    op.create_table(
        'email_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('from_email', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('to', sa.Text(), nullable=True),
        sa.Column('cc', sa.Text(), nullable=True),
        sa.Column('bcc', sa.Text(), nullable=True),
        sa.Column('total_email_sent', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('SUCCESS', 'FAILED', name='emailstatus'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.Column('created_on', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_modified_by', sa.UUID(), nullable=False),
        sa.Column('last_modified_on', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_on', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.UUID(), nullable=True),
        sa.Column('deleted', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='identity'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop email_logs table
    op.drop_table('email_logs', schema='identity')
    
    # Drop enum type
    op.execute('DROP TYPE identity.emailstatus')
