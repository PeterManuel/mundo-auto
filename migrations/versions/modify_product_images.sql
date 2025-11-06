-- Add new image column to products table
ALTER TABLE products
ADD COLUMN image TEXT;

-- Copy primary images from product_images to products (if you want to preserve existing primary images)
UPDATE products p
SET image = (
    SELECT image_data 
    FROM product_images pi 
    WHERE pi.product_id = p.id 
    AND pi.is_primary = true 
    LIMIT 1
);

-- Drop the product_images table as it's no longer needed
DROP TABLE IF EXISTS product_images;