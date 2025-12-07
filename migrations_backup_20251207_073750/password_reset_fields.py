"""Add password reset fields to users table

Revision ID: password_reset_fields
Revises: 12ac09e2c526
Create Date: 2025-11-23

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'password_reset_fields'
down_revision = '12ac09e2c526'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add password reset fields to users table
    op.add_column('users', sa.Column('reset_password_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('reset_password_expires', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove password reset fields from users table
    op.drop_column('users', 'reset_password_expires')
    op.drop_column('users', 'reset_password_token')