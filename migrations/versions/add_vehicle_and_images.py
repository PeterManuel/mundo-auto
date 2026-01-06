"""Add Vehicle and ShopProductImage models and relationships

Revision ID: add_vehicle_and_images
Revises: [latest revision]
Create Date: 2026-01-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'add_vehicle_and_images'
down_revision = None  # Replace with latest revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Create vehicles table first
    op.create_table('vehicles',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('brand', sa.String(), nullable=False),
        sa.Column('manufacturer_year', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create vehicle_models table with foreign key to vehicles
    op.create_table('vehicle_models',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('vehicle_id', UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for vehicles table
    op.create_index('ix_vehicles_brand', 'vehicles', ['brand'])
    op.create_index('ix_vehicles_manufacturer_year', 'vehicles', ['manufacturer_year'])
    
    # Create indexes for vehicle_models table
    op.create_index('ix_vehicle_models_name', 'vehicle_models', ['name'])
    op.create_index('ix_vehicle_models_vehicle_id', 'vehicle_models', ['vehicle_id'])
    
    # Create shop_product_images table
    op.create_table('shop_product_images',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('shop_product_id', UUID(as_uuid=True), nullable=False),
        sa.Column('image_data', sa.Text(), nullable=False),
        sa.Column('alt_text', sa.String(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, default=False),
        sa.Column('display_order', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['shop_product_id'], ['shop_products.id'], ondelete='CASCADE'),
    )
    
    # Create vehicle_shop_product many-to-many relationship table
    op.create_table('vehicle_shop_product',
        sa.Column('vehicle_id', UUID(as_uuid=True), nullable=False),
        sa.Column('shop_product_id', UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint('vehicle_id', 'shop_product_id'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id']),
        sa.ForeignKeyConstraint(['shop_product_id'], ['shop_products.id']),
    )
    
    # Remove the image column from shop_products table (if it exists)
    try:
        op.drop_column('shop_products', 'image')
    except:
        # Column might not exist in current schema
        pass


def downgrade():
    # Drop tables and indexes in reverse order
    op.drop_table('vehicle_shop_product')
    op.drop_table('shop_product_images')
    
    op.drop_index('ix_vehicle_models_vehicle_id', 'vehicle_models')
    op.drop_index('ix_vehicle_models_name', 'vehicle_models')
    op.drop_table('vehicle_models')
    
    op.drop_index('ix_vehicles_manufacturer_year', 'vehicles')
    op.drop_index('ix_vehicles_brand', 'vehicles')
    op.drop_table('vehicles')
    
    # Re-add image column to shop_products if needed
    op.add_column('shop_products', sa.Column('image', sa.Text(), nullable=True))