-- Script to remove product_id column from order_items table
-- This script completes the migration to autonomous shop products

-- Step 1: Drop the foreign key constraint if it exists
-- Note: Replace 'fk_order_items_product_id' with the actual constraint name if different
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'fk_order_items_product_id' 
        AND table_name = 'order_items'
    ) THEN
        ALTER TABLE order_items DROP CONSTRAINT fk_order_items_product_id;
        RAISE NOTICE 'Dropped foreign key constraint fk_order_items_product_id';
    ELSE
        RAISE NOTICE 'Foreign key constraint fk_order_items_product_id does not exist';
    END IF;
END $$;

-- Step 2: Drop any other constraints that might reference product_id
-- Check for any other constraints and drop them
DO $$ 
DECLARE
    constraint_rec RECORD;
BEGIN
    FOR constraint_rec IN 
        SELECT constraint_name 
        FROM information_schema.constraint_column_usage 
        WHERE table_name = 'order_items' 
        AND column_name = 'product_id'
    LOOP
        EXECUTE 'ALTER TABLE order_items DROP CONSTRAINT ' || constraint_rec.constraint_name;
        RAISE NOTICE 'Dropped constraint: %', constraint_rec.constraint_name;
    END LOOP;
END $$;

-- Step 3: Drop the product_id column
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'order_items' 
        AND column_name = 'product_id'
    ) THEN
        ALTER TABLE order_items DROP COLUMN product_id;
        RAISE NOTICE 'Dropped product_id column from order_items table';
    ELSE
        RAISE NOTICE 'Column product_id does not exist in order_items table';
    END IF;
END $$;

-- Step 4: Verify the column has been removed
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'order_items' 
ORDER BY ordinal_position;