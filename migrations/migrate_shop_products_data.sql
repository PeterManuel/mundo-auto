-- Data migration script to populate autonomous shop_products from existing products
-- Run this AFTER the structure migration if you have existing data to migrate

-- This script assumes you have existing shop_products records with product_id references
-- and you want to copy the product information into the shop_products table

BEGIN;

-- Step 1: Update shop_products with data from linked products
UPDATE shop_products 
SET 
    name = COALESCE(p.name, 'Unknown Product'),
    slug = COALESCE(p.slug, 'unknown') || '-shop-' || shop_products.shop_id::text || '-' || shop_products.id::text,
    description = p.description,
    technical_details = p.technical_details,
    oe_number = p.oe_number,
    brand = p.brand,
    manufacturer = p.manufacturer,
    model = p.model,
    manufacturer_year = p.manufacturer_year,
    compatible_vehicles = p.compatible_vehicles,
    weight = p.weight,
    dimensions = p.dimensions,
    image = p.image,
    is_featured = COALESCE(p.is_featured, false),
    is_on_sale = COALESCE(p.is_on_sale, false)
FROM products p 
WHERE shop_products.product_id = p.id
AND shop_products.name = 'Unknown Product'; -- Only update records that haven't been updated

-- Step 2: Copy category relationships from products to shop_products
INSERT INTO shop_product_category (shop_product_id, category_id)
SELECT DISTINCT sp.id, pc.category_id
FROM shop_products sp
JOIN products p ON sp.product_id = p.id
JOIN product_category pc ON p.id = pc.product_id
WHERE EXISTS (
    SELECT 1 FROM categories c WHERE c.id = pc.category_id
)
ON CONFLICT (shop_product_id, category_id) DO NOTHING;

-- Step 3: Handle shop_products that don't have a linked product
-- Give them default values based on any available information
UPDATE shop_products 
SET 
    name = COALESCE(NULLIF(name, ''), 'Shop Product ' || id::text),
    slug = 'product-' || id::text,
    description = 'Product managed by shop',
    is_featured = false,
    is_on_sale = false
WHERE name = 'Unknown Product' OR name IS NULL;

-- Step 4: Verify data integrity
-- Check for any shop_products without names
SELECT COUNT(*) as products_without_names
FROM shop_products 
WHERE name IS NULL OR name = '';

-- Check for duplicate slugs within the same shop (should be 0)
SELECT shop_id, slug, COUNT(*) as duplicate_count
FROM shop_products 
GROUP BY shop_id, slug 
HAVING COUNT(*) > 1;

-- Show summary of migrated data
SELECT 
    'Migration Summary' as info,
    COUNT(*) as total_shop_products,
    COUNT(CASE WHEN name != 'Unknown Product' THEN 1 END) as products_with_names,
    COUNT(CASE WHEN description IS NOT NULL THEN 1 END) as products_with_descriptions,
    COUNT(CASE WHEN brand IS NOT NULL THEN 1 END) as products_with_brands,
    COUNT(CASE WHEN oe_number IS NOT NULL THEN 1 END) as products_with_oe_numbers
FROM shop_products;

-- Show category relationships
SELECT 
    'Category Relationships' as info,
    COUNT(*) as total_relationships
FROM shop_product_category;

COMMIT;

-- Optional: After verifying the migration is successful, you can drop the product_id column
-- Uncomment the following lines only after you're sure the migration worked correctly:

/*
-- Remove the foreign key constraint (if it exists)
ALTER TABLE shop_products DROP CONSTRAINT IF EXISTS shop_products_product_id_fkey;

-- Drop the product_id column
ALTER TABLE shop_products DROP COLUMN IF EXISTS product_id;
*/

SELECT 'Data migration completed successfully!' as status;