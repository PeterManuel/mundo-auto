-- ============================================================================
-- Database Schema Updates for Vehicle and Multiple Images Implementation
-- Date: January 3, 2026
-- Description: Creates Vehicle entity, ShopProductImage entity, and relationships
-- ============================================================================

-- Create vehicles table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'vehicles' AND table_schema = current_schema()) THEN
        CREATE TABLE vehicles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            brand VARCHAR NOT NULL,
            manufacturer_year INTEGER,
            description TEXT,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now()
        );
        RAISE NOTICE 'Created vehicles table';
    ELSE
        RAISE NOTICE 'vehicles table already exists, skipping creation';
    END IF;
END $$;

-- Create vehicle_models table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'vehicle_models' AND table_schema = current_schema()) THEN
        CREATE TABLE vehicle_models (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR NOT NULL,
            description TEXT,
            vehicle_id UUID NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT fk_vehicle_models_vehicle_id 
                FOREIGN KEY (vehicle_id) 
                REFERENCES vehicles(id) 
                ON DELETE CASCADE
        );
        RAISE NOTICE 'Created vehicle_models table';
    ELSE
        RAISE NOTICE 'vehicle_models table already exists, skipping creation';
    END IF;
END $$;

-- Create indexes for vehicles table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'ix_vehicles_brand' AND schemaname = current_schema()) THEN
        CREATE INDEX ix_vehicles_brand ON vehicles(brand);
        RAISE NOTICE 'Created index ix_vehicles_brand';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'ix_vehicles_manufacturer_year' AND schemaname = current_schema()) THEN
        CREATE INDEX ix_vehicles_manufacturer_year ON vehicles(manufacturer_year);
        RAISE NOTICE 'Created index ix_vehicles_manufacturer_year';
    END IF;
END $$;

-- Create indexes for vehicle_models table  
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'ix_vehicle_models_name' AND schemaname = current_schema()) THEN
        CREATE INDEX ix_vehicle_models_name ON vehicle_models(name);
        RAISE NOTICE 'Created index ix_vehicle_models_name';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'ix_vehicle_models_vehicle_id' AND schemaname = current_schema()) THEN
        CREATE INDEX ix_vehicle_models_vehicle_id ON vehicle_models(vehicle_id);
        RAISE NOTICE 'Created index ix_vehicle_models_vehicle_id';
    END IF;
END $$;

-- Create shop_product_images table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'shop_product_images' AND table_schema = current_schema()) THEN
        CREATE TABLE shop_product_images (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            shop_product_id UUID NOT NULL,
            image_data TEXT NOT NULL,
            alt_text VARCHAR,
            is_primary BOOLEAN NOT NULL DEFAULT false,
            display_order INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
            CONSTRAINT fk_shop_product_images_shop_product_id 
                FOREIGN KEY (shop_product_id) 
                REFERENCES shop_products(id) 
                ON DELETE CASCADE
        );
        RAISE NOTICE 'Created shop_product_images table';
    ELSE
        RAISE NOTICE 'shop_product_images table already exists, skipping creation';
    END IF;
END $$;

-- Create vehicle_shop_product many-to-many relationship table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'vehicle_shop_product' AND table_schema = current_schema()) THEN
        CREATE TABLE vehicle_shop_product (
            vehicle_id UUID NOT NULL,
            shop_product_id UUID NOT NULL,
            PRIMARY KEY (vehicle_id, shop_product_id),
            CONSTRAINT fk_vehicle_shop_product_vehicle_id 
                FOREIGN KEY (vehicle_id) 
                REFERENCES vehicles(id) 
                ON DELETE CASCADE,
            CONSTRAINT fk_vehicle_shop_product_shop_product_id 
                FOREIGN KEY (shop_product_id) 
                REFERENCES shop_products(id) 
                ON DELETE CASCADE
        );
        RAISE NOTICE 'Created vehicle_shop_product table';
    ELSE
        RAISE NOTICE 'vehicle_shop_product table already exists, skipping creation';
    END IF;
END $$;

-- Remove the image column from shop_products table (if it exists)
-- This is wrapped in a DO block to handle the case where the column might not exist
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'shop_products' 
        AND column_name = 'image'
        AND table_schema = current_schema()
    ) THEN
        ALTER TABLE shop_products DROP COLUMN image;
        RAISE NOTICE 'Dropped image column from shop_products table';
    ELSE
        RAISE NOTICE 'Image column does not exist in shop_products table, skipping drop';
    END IF;
END $$;

-- Create indexes for better query performance
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_shop_product_images_shop_product_id' AND schemaname = current_schema()) THEN
        CREATE INDEX idx_shop_product_images_shop_product_id ON shop_product_images(shop_product_id);
        RAISE NOTICE 'Created index idx_shop_product_images_shop_product_id';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_shop_product_images_is_primary' AND schemaname = current_schema()) THEN
        CREATE INDEX idx_shop_product_images_is_primary ON shop_product_images(is_primary);
        RAISE NOTICE 'Created index idx_shop_product_images_is_primary';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_shop_product_images_display_order' AND schemaname = current_schema()) THEN
        CREATE INDEX idx_shop_product_images_display_order ON shop_product_images(display_order);
        RAISE NOTICE 'Created index idx_shop_product_images_display_order';
    END IF;
END $$;

-- Create indexes for the many-to-many relationship tables
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_vehicle_shop_product_vehicle_id' AND schemaname = current_schema()) THEN
        CREATE INDEX idx_vehicle_shop_product_vehicle_id ON vehicle_shop_product(vehicle_id);
        RAISE NOTICE 'Created index idx_vehicle_shop_product_vehicle_id';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_vehicle_shop_product_shop_product_id' AND schemaname = current_schema()) THEN
        CREATE INDEX idx_vehicle_shop_product_shop_product_id ON vehicle_shop_product(shop_product_id);
        RAISE NOTICE 'Created index idx_vehicle_shop_product_shop_product_id';
    END IF;
END $$;

-- Add comments for documentation
COMMENT ON TABLE vehicle_models IS 'Vehicle models (e.g., Corolla, F-150, 3 Series) - each model belongs to a vehicle';
COMMENT ON TABLE vehicles IS 'Vehicle entity with brand - can have multiple models';
COMMENT ON TABLE shop_product_images IS 'Multiple images for shop products with ordering and primary image support';
COMMENT ON TABLE vehicle_shop_product IS 'Many-to-many relationship between vehicles and shop products';

COMMENT ON COLUMN vehicle_models.name IS 'Vehicle model name (e.g., Corolla, F-150, 3 Series)';
COMMENT ON COLUMN vehicle_models.vehicle_id IS 'Foreign key to parent vehicle';
COMMENT ON COLUMN vehicles.brand IS 'Vehicle brand/manufacturer name (e.g., Toyota, Ford, BMW)';
COMMENT ON COLUMN vehicles.manufacturer_year IS 'Year the vehicle was manufactured';

COMMENT ON COLUMN shop_product_images.image_data IS 'Base64 encoded image data';
COMMENT ON COLUMN shop_product_images.alt_text IS 'Alt text for accessibility';
COMMENT ON COLUMN shop_product_images.is_primary IS 'Whether this is the primary/featured image';
COMMENT ON COLUMN shop_product_images.display_order IS 'Order for displaying images (0 = first)';

-- Optional: Create a function to automatically update the updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at for vehicle_models
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_vehicle_models_updated_at') THEN
        CREATE TRIGGER update_vehicle_models_updated_at 
            BEFORE UPDATE ON vehicle_models 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_vehicle_models_updated_at';
    END IF;
END $$;

-- Create trigger to automatically update updated_at for vehicles
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_vehicles_updated_at') THEN
        CREATE TRIGGER update_vehicles_updated_at 
            BEFORE UPDATE ON vehicles 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_vehicles_updated_at';
    END IF;
END $$;

-- Verify the changes
SELECT 'Tables created successfully. Verifying...' AS status;

-- Check if tables exist
SELECT 
    table_name,
    CASE 
        WHEN table_name IN ('vehicle_models', 'vehicles', 'shop_product_images', 'vehicle_shop_product') 
        THEN 'NEW TABLE ✓' 
        ELSE 'EXISTING' 
    END AS table_status
FROM information_schema.tables 
WHERE table_schema = current_schema() 
AND table_name IN ('vehicle_models', 'vehicles', 'shop_product_images', 'vehicle_shop_product', 'shop_products')
ORDER BY table_name;

-- Check indexes
SELECT 
    indexname,
    tablename
FROM pg_indexes 
WHERE schemaname = current_schema() 
AND (tablename IN ('vehicle_models', 'vehicles', 'shop_product_images', 'vehicle_shop_product')
     OR indexname LIKE '%vehicle_models%' 
     OR indexname LIKE '%vehicles%' 
     OR indexname LIKE '%shop_product_images%'
     OR indexname LIKE '%vehicle_shop_product%')
ORDER BY tablename, indexname;

-- ============================================================================
-- End of schema updates
-- ============================================================================