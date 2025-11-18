-- Migration script to update order_items table
-- This script updates the order_items table to use shop_product_id instead of separate product_id and shop_id

-- Step 1: Add the new shop_product_id column
ALTER TABLE order_items 
ADD COLUMN shop_product_id UUID;

-- Step 2: Add foreign key constraint for the new column
ALTER TABLE order_items 
ADD CONSTRAINT fk_order_items_shop_product_id 
FOREIGN KEY (shop_product_id) REFERENCES shop_products(id);

-- Step 3: Update existing records to populate shop_product_id
-- This assumes that there are shop_products that match the product_id and shop_id combinations
UPDATE order_items 
SET shop_product_id = sp.id
FROM shop_products sp
WHERE sp.shop_id = order_items.shop_id 
  AND EXISTS (
    SELECT 1 FROM products p 
    WHERE p.id = order_items.product_id 
      AND (p.name = sp.name OR p.oe_number = sp.oe_number)
  );

-- Step 4: For any remaining NULL shop_product_id records, you might need to handle them manually
-- Check if there are any unmatched records
SELECT COUNT(*) as unmatched_records 
FROM order_items 
WHERE shop_product_id IS NULL;

-- Step 5: Make shop_product_id NOT NULL (only after ensuring all records have values)
-- Uncomment the following line after verifying all records are properly updated:
-- ALTER TABLE order_items ALTER COLUMN shop_product_id SET NOT NULL;

-- Step 6: Drop the old columns and their constraints
-- Uncomment these lines after verifying the migration worked correctly:
-- ALTER TABLE order_items DROP CONSTRAINT IF EXISTS fk_order_items_product_id;
-- ALTER TABLE order_items DROP CONSTRAINT IF EXISTS fk_order_items_shop_id;
-- ALTER TABLE order_items DROP COLUMN product_id;
-- ALTER TABLE order_items DROP COLUMN shop_id;

-- Step 7: Verify the migration
SELECT 
    oi.id,
    oi.order_id,
    oi.shop_product_id,
    oi.product_name,
    oi.shop_name,
    sp.name as actual_product_name,
    s.name as actual_shop_name
FROM order_items oi
LEFT JOIN shop_products sp ON oi.shop_product_id = sp.id
LEFT JOIN shops s ON sp.shop_id = s.id
LIMIT 10;