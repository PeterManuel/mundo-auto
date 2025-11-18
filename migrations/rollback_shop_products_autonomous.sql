-- Rollback script for shop_products autonomous migration
-- WARNING: This will remove data that was added to make shop_products autonomous
-- Make sure to backup your data before running this rollback

-- Drop the trigger and function
DROP TRIGGER IF EXISTS ensure_shop_product_slug_unique_trigger ON shop_products;
DROP FUNCTION IF EXISTS ensure_shop_product_slug_unique();

-- Drop the shop_product_category table
DROP TABLE IF EXISTS shop_product_category;

-- Remove all the added columns from shop_products
ALTER TABLE shop_products 
DROP COLUMN IF EXISTS name,
DROP COLUMN IF EXISTS slug,
DROP COLUMN IF EXISTS description,
DROP COLUMN IF EXISTS technical_details,
DROP COLUMN IF EXISTS oe_number,
DROP COLUMN IF EXISTS brand,
DROP COLUMN IF EXISTS manufacturer,
DROP COLUMN IF EXISTS model,
DROP COLUMN IF EXISTS manufacturer_year,
DROP COLUMN IF EXISTS compatible_vehicles,
DROP COLUMN IF EXISTS weight,
DROP COLUMN IF EXISTS dimensions,
DROP COLUMN IF EXISTS image,
DROP COLUMN IF EXISTS is_featured,
DROP COLUMN IF EXISTS is_on_sale;

-- Make price column nullable again (if needed)
ALTER TABLE shop_products ALTER COLUMN price DROP NOT NULL;

-- Restore the foreign key constraint to products table (if needed)
-- Uncomment if you want to restore the relationship with products table
-- ALTER TABLE shop_products ADD CONSTRAINT shop_products_product_id_fkey 
-- FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;

-- Drop all the indexes we created
DROP INDEX IF EXISTS idx_shop_products_name;
DROP INDEX IF EXISTS idx_shop_products_slug;
DROP INDEX IF EXISTS idx_shop_products_oe_number;
DROP INDEX IF EXISTS idx_shop_products_brand;
DROP INDEX IF EXISTS idx_shop_products_model;
DROP INDEX IF EXISTS idx_shop_products_manufacturer_year;
DROP INDEX IF EXISTS idx_shop_products_is_featured;
DROP INDEX IF EXISTS idx_shop_products_is_on_sale;
DROP INDEX IF EXISTS idx_shop_products_shop_active;
DROP INDEX IF EXISTS idx_shop_products_shop_slug;

SELECT 'Rollback completed. Shop products are no longer autonomous.' as status;

-- Show the reverted table structure
\d shop_products