-- Rollback Script: Revert ShopProduct relationship from VehicleModel back to Vehicle
-- This script rolls back the vehicle_model_shop_product table to vehicle_shop_product table
-- Date: 2026-01-09

-- Step 1: Recreate the vehicle_shop_product table
CREATE TABLE IF NOT EXISTS vehicle_shop_product (
    vehicle_id UUID NOT NULL REFERENCES vehicles(id),
    shop_product_id UUID NOT NULL REFERENCES shop_products(id),
    PRIMARY KEY (vehicle_id, shop_product_id)
);

-- Step 2: Migrate data back from vehicle_model_shop_product to vehicle_shop_product
-- For each vehicle_model-shop_product relationship, get the vehicle and create the relationship
INSERT INTO vehicle_shop_product (vehicle_id, shop_product_id)
SELECT DISTINCT vm.vehicle_id, vmsp.shop_product_id
FROM vehicle_model_shop_product vmsp
JOIN vehicle_models vm ON vm.id = vmsp.vehicle_model_id
ON CONFLICT (vehicle_id, shop_product_id) DO NOTHING;

-- Step 3: Verify the rollback (check counts)
-- Run these SELECT statements to verify data migrated correctly:
-- SELECT COUNT(*) as new_relationships FROM vehicle_shop_product;
-- SELECT COUNT(*) as old_relationships FROM vehicle_model_shop_product;

-- Step 4: Drop the vehicle_model_shop_product table (only after verifying rollback)
-- WARNING: Make sure to backup your data before running this!
DROP TABLE IF EXISTS vehicle_model_shop_product;

-- Done!
