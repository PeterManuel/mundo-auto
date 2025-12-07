"""modify product images

Revision ID: modify_product_images
Revises: 12ac09e2c526
Create Date: 2025-11-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'modify_product_images'
down_revision = '12ac09e2c526'  # The current head revision
branch_labels = None
depends_on = None

def upgrade():
    # Add image column to products table
    op.add_column('products', sa.Column('image', sa.Text(), nullable=True))
    
    # Copy primary images from product_images to products
    op.execute("""
        UPDATE products p
        SET image = (
            SELECT image_data 
            FROM product_images pi 
            WHERE pi.product_id = p.id 
            AND pi.is_primary = true 
            LIMIT 1
        )
    """)
    
    # Drop product_images table
    op.drop_table('product_images')

def downgrade():
    # Create product_images table
    op.create_table('product_images',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('product_id', postgresql.UUID(), nullable=False),
        sa.Column('image_data', sa.Text(), nullable=False),
        sa.Column('alt_text', sa.String(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy images back from products to product_images
    op.execute("""
        INSERT INTO product_images (id, product_id, image_data, is_primary, created_at)
        SELECT 
            gen_random_uuid(),
            id,
            image,
            true,
            NOW()
        FROM products
        WHERE image IS NOT NULL
    """)
    
    # Remove image column from products
    op.drop_column('products', 'image')