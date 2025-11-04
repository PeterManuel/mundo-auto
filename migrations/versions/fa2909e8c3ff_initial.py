"""initial

Revision ID: fa2909e8c3ff
Revises: 
Create Date: 2025-10-25 13:26:05.491265

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa2909e8c3ff'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add model and manufacturer_year columns to products table
    op.add_column('products', sa.Column('model', sa.String(), nullable=True))
    op.add_column('products', sa.Column('manufacturer_year', sa.Integer(), nullable=True))
    
    # Create index on model column
    op.create_index(op.f('ix_products_model'), 'products', ['model'], unique=False)


def downgrade() -> None:
    # Remove index and columns
    op.drop_index(op.f('ix_products_model'), table_name='products')
    op.drop_column('products', 'manufacturer_year')
    op.drop_column('products', 'model')