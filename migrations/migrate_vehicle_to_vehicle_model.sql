-- Migration Script: Change ShopProduct relationship from Vehicle to VehicleModel
-- This script migrates the vehicle_shop_product table to vehicle_model_shop_product table
-- Date: 2026-01-09

-- Step 1: Create the new vehicle_model_shop_product table
CREATE TABLE IF NOT EXISTS vehicle_model_shop_product (
    vehicle_model_id UUID NOT NULL REFERENCES vehicle_models(id),
    shop_product_id UUID NOT NULL REFERENCES shop_products(id),
    PRIMARY KEY (vehicle_model_id, shop_product_id)
);

-- Step 2: Migrate existing data from vehicle_shop_product to vehicle_model_shop_product
-- For each vehicle-shop_product relationship, create relationships with all models of that vehicle
INSERT INTO vehicle_model_shop_product (vehicle_model_id, shop_product_id)
SELECT DISTINCT vm.id, vsp.shop_product_id
FROM vehicle_shop_product vsp
JOIN vehicle_models vm ON vm.vehicle_id = vsp.vehicle_id
ON CONFLICT (vehicle_model_id, shop_product_id) DO NOTHING;

-- Step 3: Verify the migration (check counts)
-- Run these SELECT statements to verify data migrated correctly:
-- SELECT COUNT(*) as old_relationships FROM vehicle_shop_product;
-- SELECT COUNT(*) as new_relationships FROM vehicle_model_shop_product;

-- Step 4: Drop the old table (only after verifying migration)
-- WARNING: Make sure to backup your data before running this!
DROP TABLE IF EXISTS vehicle_shop_product;

-- Done!
