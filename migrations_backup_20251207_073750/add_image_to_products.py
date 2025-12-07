"""add image to products

Revision ID: add_image_to_products
Revises: 12ac09e2c526
Create Date: 2025-11-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_image_to_products'
down_revision = '12ac09e2c526'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add image column to products table
    op.add_column('products', sa.Column('image', sa.Text(), nullable=True))
    
    # Drop product_images table if it exists
    op.drop_table('product_images')


def downgrade() -> None:
    # Create product_images table
    op.create_table('product_images',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('image_data', sa.Text(), nullable=False),
        sa.Column('alt_text', sa.String(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Remove image column from products
    op.drop_column('products', 'image')