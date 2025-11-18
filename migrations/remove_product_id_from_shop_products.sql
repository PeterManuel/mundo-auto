-- Migration to remove product_id column from shop_products table
-- This column is no longer needed since shop_products are now autonomous

-- First, drop any foreign key constraints related to product_id
ALTER TABLE shop_products DROP CONSTRAINT IF EXISTS shop_products_product_id_fkey;

-- Drop any indexes related to product_id
DROP INDEX IF EXISTS idx_shop_products_product_id;

-- Remove the product_id column
ALTER TABLE shop_products DROP COLUMN IF EXISTS product_id;

-- Add a comment to document this change
COMMENT ON TABLE shop_products IS 'Autonomous shop products table - no longer dependent on products table';