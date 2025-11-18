-- Rollback script for order_items migration
-- Use this script if you need to rollback the changes

-- Step 1: Add back the old columns
ALTER TABLE order_items 
ADD COLUMN product_id UUID,
ADD COLUMN shop_id UUID;

-- Step 2: Populate the old columns from shop_product relationships
UPDATE order_items 
SET shop_id = sp.shop_id
FROM shop_products sp
WHERE sp.id = order_items.shop_product_id;

-- For product_id, we'll need to create a mapping based on product names or OE numbers
-- This is more complex since we moved to autonomous shop products
-- You might need to manually handle this based on your specific data

-- Step 3: Add back foreign key constraints
ALTER TABLE order_items 
ADD CONSTRAINT fk_order_items_shop_id 
FOREIGN KEY (shop_id) REFERENCES shops(id);

-- Note: Adding back product_id foreign key might be complex if products were removed
-- ALTER TABLE order_items 
-- ADD CONSTRAINT fk_order_items_product_id 
-- FOREIGN KEY (product_id) REFERENCES products(id);

-- Step 4: Make columns NOT NULL (after populating them)
-- ALTER TABLE order_items ALTER COLUMN product_id SET NOT NULL;
-- ALTER TABLE order_items ALTER COLUMN shop_id SET NOT NULL;

-- Step 5: Drop the shop_product_id column
-- ALTER TABLE order_items DROP CONSTRAINT fk_order_items_shop_product_id;
-- ALTER TABLE order_items DROP COLUMN shop_product_id;