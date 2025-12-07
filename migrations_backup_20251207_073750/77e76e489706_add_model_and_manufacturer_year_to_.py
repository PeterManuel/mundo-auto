"""add_model_and_manufacturer_year_to_products_v2

Revision ID: 77e76e489706
Revises: fa2909e8c3ff
Create Date: 2025-10-25 13:18:57.611707

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '77e76e489706'
down_revision = 'fa2909e8c3ff'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to products table
    op.add_column('products', sa.Column('model', sa.String(), nullable=True))
    op.add_column('products', sa.Column('manufacturer_year', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_products_model'), 'products', ['model'], unique=False)


def downgrade() -> None:
    # Remove columns from products table
    op.drop_index(op.f('ix_products_model'), table_name='products')
    op.drop_column('products', 'manufacturer_year')
    op.drop_column('products', 'model')