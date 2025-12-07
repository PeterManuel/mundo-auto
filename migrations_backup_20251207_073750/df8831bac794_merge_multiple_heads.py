"""merge multiple heads

Revision ID: df8831bac794
Revises: add_image_to_products, make_shop_products_autonomous, modify_product_images, password_reset_fields
Create Date: 2025-12-07 07:34:38.820522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df8831bac794'
down_revision = ('add_image_to_products', 'make_shop_products_autonomous', 'modify_product_images', 'password_reset_fields')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass