"""add_indexes_identity_logger

Revision ID: 2b3c4d5e6f7
Revises: d78cd28231e6
Create Date: 2026-02-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2b3c4d5e6f7'
down_revision = 'd78cd28231e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema: create indexes."""
    # users.phone_number
    op.create_index('ix_users_phone_number', 'users', ['phone_number'], schema='identity')

    # user_roles composite (role_id, user_id)
    op.create_index('ix_user_roles_role_id_user_id', 'user_roles', ['role_id', 'user_id'], schema='identity')

    # roles.is_system
    op.create_index('ix_roles_is_system', 'roles', ['is_system'], schema='identity')

    # email_logs.status
    op.create_index('ix_email_logs_status', 'email_logs', ['status'], schema='logger')


def downgrade() -> None:
    """Downgrade schema: drop indexes."""
    op.drop_index('ix_email_logs_status', table_name='email_logs', schema='logger')
    op.drop_index('ix_roles_is_system', table_name='roles', schema='identity')
    op.drop_index('ix_user_roles_role_id_user_id', table_name='user_roles', schema='identity')
    op.drop_index('ix_users_phone_number', table_name='users', schema='identity')
