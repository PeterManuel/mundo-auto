"""Merge multiple heads

Revision ID: 12ac09e2c526
Revises: 7dd44ee1e9f6, add_banner_table
Create Date: 2025-11-05 07:13:59.800216

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '12ac09e2c526'
down_revision = ('7dd44ee1e9f6', 'add_banner_table')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass