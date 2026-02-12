"""add_audit_logs_table

Revision ID: 2ffac5349efa
Revises: 2b3c4d5e6f7
Create Date: 2026-02-12 09:48:02.260084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ffac5349efa'
down_revision: Union[str, Sequence[str], None] = '2b3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Intentionally only create the audit_logs table. Other autogen
    # operations were spurious due to DB/revision mismatch and have been
    # removed to avoid dropping application objects.
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('type', sa.String(length=32), nullable=False),
        sa.Column('table_name', sa.String(length=255), nullable=True),
        sa.Column('date_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('affected_columns', sa.JSON(), nullable=True),
        sa.Column('primary_key', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='logger',
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Intentionally only drop the audit_logs table on downgrade.
    op.drop_table('audit_logs', schema='logger')
