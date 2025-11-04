"""add_model_and_manufacturer_year_columns

Revision ID: 7dd44ee1e9f6
Revises: 77e76e489706
Create Date: 2025-10-25 13:23:38.571485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7dd44ee1e9f6'
down_revision = '77e76e489706'
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