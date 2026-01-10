"""Migrate vehicle_shop_product to vehicle_model_shop_product

This migration changes the ShopProduct relationship from Vehicle to VehicleModel.

Revision ID: migrate_vehicle_model
Revises: 
Create Date: 2026-01-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'migrate_vehicle_model'
down_revision: Union[str, None] = None  # Update this to your current head revision
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the new vehicle_model_shop_product table
    op.create_table(
        'vehicle_model_shop_product',
        sa.Column('vehicle_model_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicle_models.id'), primary_key=True),
        sa.Column('shop_product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('shop_products.id'), primary_key=True)
    )
    
    # Migrate existing data from vehicle_shop_product to vehicle_model_shop_product
    # For each vehicle-shop_product relationship, create relationships with all models of that vehicle
    op.execute("""
        INSERT INTO vehicle_model_shop_product (vehicle_model_id, shop_product_id)
        SELECT DISTINCT vm.id, vsp.shop_product_id
        FROM vehicle_shop_product vsp
        JOIN vehicle_models vm ON vm.vehicle_id = vsp.vehicle_id
    """)
    
    # Drop the old vehicle_shop_product table
    op.drop_table('vehicle_shop_product')


def downgrade() -> None:
    # Recreate the vehicle_shop_product table
    op.create_table(
        'vehicle_shop_product',
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id'), primary_key=True),
        sa.Column('shop_product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('shop_products.id'), primary_key=True)
    )
    
    # Migrate data back from vehicle_model_shop_product to vehicle_shop_product
    # For each vehicle_model-shop_product relationship, get the vehicle and create the relationship
    op.execute("""
        INSERT INTO vehicle_shop_product (vehicle_id, shop_product_id)
        SELECT DISTINCT vm.vehicle_id, vmsp.shop_product_id
        FROM vehicle_model_shop_product vmsp
        JOIN vehicle_models vm ON vm.id = vmsp.vehicle_model_id
    """)
    
    # Drop the vehicle_model_shop_product table
    op.drop_table('vehicle_model_shop_product')
