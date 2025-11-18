"""Make shop_products autonomous from products

Revision ID: make_shop_products_autonomous
Revises: <previous_revision_id>
Create Date: 2024-11-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'make_shop_products_autonomous'
down_revision = '<previous_revision_id>'  # Replace with your actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    # Create the shop_product_category junction table
    op.create_table('shop_product_category',
        sa.Column('shop_product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['shop_product_id'], ['shop_products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('shop_product_id', 'category_id')
    )
    
    # Create indexes for the junction table
    op.create_index('idx_shop_product_category_shop_product_id', 'shop_product_category', ['shop_product_id'])
    op.create_index('idx_shop_product_category_category_id', 'shop_product_category', ['category_id'])
    
    # Add all product-related columns to shop_products
    op.add_column('shop_products', sa.Column('name', sa.String(), nullable=False, server_default='Unknown Product'))
    op.add_column('shop_products', sa.Column('slug', sa.String(), nullable=False, server_default='unknown-product'))
    op.add_column('shop_products', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('shop_products', sa.Column('technical_details', sa.Text(), nullable=True))
    op.add_column('shop_products', sa.Column('oe_number', sa.String(), nullable=True))
    op.add_column('shop_products', sa.Column('brand', sa.String(), nullable=True))
    op.add_column('shop_products', sa.Column('manufacturer', sa.String(), nullable=True))
    op.add_column('shop_products', sa.Column('model', sa.String(), nullable=True))
    op.add_column('shop_products', sa.Column('manufacturer_year', sa.Integer(), nullable=True))
    op.add_column('shop_products', sa.Column('compatible_vehicles', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('shop_products', sa.Column('weight', sa.Float(), nullable=True))
    op.add_column('shop_products', sa.Column('dimensions', sa.String(), nullable=True))
    op.add_column('shop_products', sa.Column('image', sa.Text(), nullable=True))
    op.add_column('shop_products', sa.Column('is_featured', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('shop_products', sa.Column('is_on_sale', sa.Boolean(), nullable=False, server_default='false'))
    
    # Make price column NOT NULL
    op.execute("UPDATE shop_products SET price = 0.00 WHERE price IS NULL")
    op.alter_column('shop_products', 'price', nullable=False)
    
    # Create indexes for better performance
    op.create_index('idx_shop_products_name', 'shop_products', ['name'])
    op.create_index('idx_shop_products_slug', 'shop_products', ['slug'])
    op.create_index('idx_shop_products_oe_number', 'shop_products', ['oe_number'])
    op.create_index('idx_shop_products_brand', 'shop_products', ['brand'])
    op.create_index('idx_shop_products_model', 'shop_products', ['model'])
    op.create_index('idx_shop_products_manufacturer_year', 'shop_products', ['manufacturer_year'])
    op.create_index('idx_shop_products_is_featured', 'shop_products', ['is_featured'])
    op.create_index('idx_shop_products_is_on_sale', 'shop_products', ['is_on_sale'])
    op.create_index('idx_shop_products_shop_active', 'shop_products', ['shop_id', 'is_active'])
    op.create_index('idx_shop_products_shop_slug', 'shop_products', ['shop_id', 'slug'])
    
    # Create function for slug uniqueness
    op.execute("""
        CREATE OR REPLACE FUNCTION ensure_shop_product_slug_unique()
        RETURNS TRIGGER AS $$
        DECLARE
            base_slug TEXT;
            counter INTEGER := 1;
            new_slug TEXT;
        BEGIN
            -- If slug is not provided, generate from name
            IF NEW.slug IS NULL OR NEW.slug = '' THEN
                -- Simple slugify function (replace spaces with hyphens, lowercase)
                base_slug := lower(trim(regexp_replace(NEW.name, '[^a-zA-Z0-9\\s]', '', 'g')));
                base_slug := regexp_replace(base_slug, '\\s+', '-', 'g');
                NEW.slug := base_slug;
            ELSE
                base_slug := NEW.slug;
            END IF;
            
            new_slug := base_slug;
            
            -- Ensure uniqueness within the shop
            WHILE EXISTS (
                SELECT 1 FROM shop_products 
                WHERE shop_id = NEW.shop_id 
                AND slug = new_slug 
                AND (NEW.id IS NULL OR id != NEW.id)
            ) LOOP
                new_slug := base_slug || '-' || counter;
                counter := counter + 1;
            END LOOP;
            
            NEW.slug := new_slug;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Create trigger for slug uniqueness
    op.execute("""
        CREATE TRIGGER ensure_shop_product_slug_unique_trigger
            BEFORE INSERT OR UPDATE ON shop_products
            FOR EACH ROW
            EXECUTE FUNCTION ensure_shop_product_slug_unique();
    """)
    
    # Remove default values after creation (optional)
    op.alter_column('shop_products', 'name', server_default=None)
    op.alter_column('shop_products', 'slug', server_default=None)
    op.alter_column('shop_products', 'is_featured', server_default=None)
    op.alter_column('shop_products', 'is_on_sale', server_default=None)


def downgrade():
    # Drop trigger and function
    op.execute("DROP TRIGGER IF EXISTS ensure_shop_product_slug_unique_trigger ON shop_products")
    op.execute("DROP FUNCTION IF EXISTS ensure_shop_product_slug_unique()")
    
    # Drop indexes
    op.drop_index('idx_shop_products_shop_slug', table_name='shop_products')
    op.drop_index('idx_shop_products_shop_active', table_name='shop_products')
    op.drop_index('idx_shop_products_is_on_sale', table_name='shop_products')
    op.drop_index('idx_shop_products_is_featured', table_name='shop_products')
    op.drop_index('idx_shop_products_manufacturer_year', table_name='shop_products')
    op.drop_index('idx_shop_products_model', table_name='shop_products')
    op.drop_index('idx_shop_products_brand', table_name='shop_products')
    op.drop_index('idx_shop_products_oe_number', table_name='shop_products')
    op.drop_index('idx_shop_products_slug', table_name='shop_products')
    op.drop_index('idx_shop_products_name', table_name='shop_products')
    
    # Make price column nullable again
    op.alter_column('shop_products', 'price', nullable=True)
    
    # Remove all added columns
    op.drop_column('shop_products', 'is_on_sale')
    op.drop_column('shop_products', 'is_featured')
    op.drop_column('shop_products', 'image')
    op.drop_column('shop_products', 'dimensions')
    op.drop_column('shop_products', 'weight')
    op.drop_column('shop_products', 'compatible_vehicles')
    op.drop_column('shop_products', 'manufacturer_year')
    op.drop_column('shop_products', 'model')
    op.drop_column('shop_products', 'manufacturer')
    op.drop_column('shop_products', 'brand')
    op.drop_column('shop_products', 'oe_number')
    op.drop_column('shop_products', 'technical_details')
    op.drop_column('shop_products', 'description')
    op.drop_column('shop_products', 'slug')
    op.drop_column('shop_products', 'name')
    
    # Drop junction table indexes
    op.drop_index('idx_shop_product_category_category_id', table_name='shop_product_category')
    op.drop_index('idx_shop_product_category_shop_product_id', table_name='shop_product_category')
    
    # Drop junction table
    op.drop_table('shop_product_category')