-- Migration script to make shop_products autonomous from products table
-- This script adds all product attributes directly to shop_products table
-- and creates the new shop_product_category junction table

-- First, create the shop_product_category junction table
CREATE TABLE IF NOT EXISTS shop_product_category (
    shop_product_id UUID NOT NULL,
    category_id UUID NOT NULL,
    PRIMARY KEY (shop_product_id, category_id),
    FOREIGN KEY (shop_product_id) REFERENCES shop_products(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_shop_product_category_shop_product_id ON shop_product_category(shop_product_id);
CREATE INDEX IF NOT EXISTS idx_shop_product_category_category_id ON shop_product_category(category_id);

-- Add all product-related columns to shop_products table
ALTER TABLE shop_products 
ADD COLUMN IF NOT EXISTS name VARCHAR NOT NULL DEFAULT 'Unknown Product',
ADD COLUMN IF NOT EXISTS slug VARCHAR NOT NULL DEFAULT 'unknown-product',
ADD COLUMN IF NOT EXISTS description TEXT,
ADD COLUMN IF NOT EXISTS technical_details TEXT,
ADD COLUMN IF NOT EXISTS oe_number VARCHAR,
ADD COLUMN IF NOT EXISTS brand VARCHAR,
ADD COLUMN IF NOT EXISTS manufacturer VARCHAR,
ADD COLUMN IF NOT EXISTS model VARCHAR,
ADD COLUMN IF NOT EXISTS manufacturer_year INTEGER,
ADD COLUMN IF NOT EXISTS compatible_vehicles TEXT[], -- PostgreSQL array
ADD COLUMN IF NOT EXISTS weight DECIMAL(10,3), -- Weight in kg with 3 decimal precision
ADD COLUMN IF NOT EXISTS dimensions VARCHAR, -- Format: "LxWxH" in cm
ADD COLUMN IF NOT EXISTS image TEXT, -- Base64 encoded image
ADD COLUMN IF NOT EXISTS is_featured BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_on_sale BOOLEAN NOT NULL DEFAULT FALSE;

-- Make price column NOT NULL (it was nullable before)
-- First update any NULL prices with a default value
UPDATE shop_products SET price = 0.00 WHERE price IS NULL;
ALTER TABLE shop_products ALTER COLUMN price SET NOT NULL;

-- Add indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_shop_products_name ON shop_products(name);
CREATE INDEX IF NOT EXISTS idx_shop_products_slug ON shop_products(slug);
CREATE INDEX IF NOT EXISTS idx_shop_products_oe_number ON shop_products(oe_number) WHERE oe_number IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_shop_products_brand ON shop_products(brand) WHERE brand IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_shop_products_model ON shop_products(model) WHERE model IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_shop_products_manufacturer_year ON shop_products(manufacturer_year) WHERE manufacturer_year IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_shop_products_is_featured ON shop_products(is_featured) WHERE is_featured = TRUE;
CREATE INDEX IF NOT EXISTS idx_shop_products_is_on_sale ON shop_products(is_on_sale) WHERE is_on_sale = TRUE;
CREATE INDEX IF NOT EXISTS idx_shop_products_shop_active ON shop_products(shop_id, is_active);

-- Create composite index for shop_id and slug (for uniqueness within shop)
CREATE INDEX IF NOT EXISTS idx_shop_products_shop_slug ON shop_products(shop_id, slug);

-- Optional: Migrate existing data from products table if it exists
-- This section can be customized based on your current data structure
-- Uncomment and modify as needed:

/*
-- Example migration of existing data (if you have products linked to shop_products)
UPDATE shop_products 
SET 
    name = p.name,
    slug = p.slug || '-' || shop_products.id::text, -- Make slug unique per shop
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
    is_featured = p.is_featured,
    is_on_sale = p.is_on_sale
FROM products p 
WHERE shop_products.product_id = p.id
AND shop_products.name = 'Unknown Product'; -- Only update records that haven't been updated yet

-- Migrate category relationships
INSERT INTO shop_product_category (shop_product_id, category_id)
SELECT DISTINCT sp.id, pc.category_id
FROM shop_products sp
JOIN products p ON sp.product_id = p.id
JOIN product_category pc ON p.id = pc.product_id
ON CONFLICT DO NOTHING;
*/

-- Remove the foreign key constraint to product_id (if it exists)
-- Note: Adjust the constraint name based on your actual constraint name
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'shop_products_product_id_fkey' 
        AND table_name = 'shop_products'
    ) THEN
        ALTER TABLE shop_products DROP CONSTRAINT shop_products_product_id_fkey;
    END IF;
END $$;

-- Optional: Drop the product_id column entirely (uncomment if you want to remove it completely)
-- ALTER TABLE shop_products DROP COLUMN IF EXISTS product_id;

-- Update the categories table to include the relationship with shop_products
-- This is handled by the ORM relationship, but you can add constraints if needed

-- Create a function to ensure slug uniqueness within each shop
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
        base_slug := lower(trim(regexp_replace(NEW.name, '[^a-zA-Z0-9\s]', '', 'g')));
        base_slug := regexp_replace(base_slug, '\s+', '-', 'g');
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

-- Create trigger to ensure slug uniqueness
DROP TRIGGER IF EXISTS ensure_shop_product_slug_unique_trigger ON shop_products;
CREATE TRIGGER ensure_shop_product_slug_unique_trigger
    BEFORE INSERT OR UPDATE ON shop_products
    FOR EACH ROW
    EXECUTE FUNCTION ensure_shop_product_slug_unique();

-- Add comments to document the changes
COMMENT ON TABLE shop_product_category IS 'Junction table linking shop products to categories';
COMMENT ON COLUMN shop_products.name IS 'Product name - now autonomous per shop';
COMMENT ON COLUMN shop_products.slug IS 'Product slug - unique within each shop';
COMMENT ON COLUMN shop_products.description IS 'Product description - shop-specific';
COMMENT ON COLUMN shop_products.technical_details IS 'Technical details - shop-specific';
COMMENT ON COLUMN shop_products.oe_number IS 'Original Equipment number';
COMMENT ON COLUMN shop_products.brand IS 'Product brand';
COMMENT ON COLUMN shop_products.manufacturer IS 'Product manufacturer';
COMMENT ON COLUMN shop_products.model IS 'Vehicle model compatibility';
COMMENT ON COLUMN shop_products.manufacturer_year IS 'Vehicle manufacturer year';
COMMENT ON COLUMN shop_products.compatible_vehicles IS 'Array of compatible vehicles';
COMMENT ON COLUMN shop_products.weight IS 'Product weight in kg';
COMMENT ON COLUMN shop_products.dimensions IS 'Product dimensions in format LxWxH (cm)';
COMMENT ON COLUMN shop_products.image IS 'Base64 encoded product image';
COMMENT ON COLUMN shop_products.is_featured IS 'Whether product is featured by the shop';
COMMENT ON COLUMN shop_products.is_on_sale IS 'Whether product is on sale by the shop';

-- Verify the migration
SELECT 'Migration completed successfully. Shop products are now autonomous.' as status;

-- Show the updated table structure
\d shop_products