# Shop Products Autonomous Migration

This directory contains migration scripts to make the `shop_products` table autonomous from the `products` table. After this migration, each shop can manage its own product catalog independently.

## Migration Files

### 1. `update_shop_products_autonomous.sql`
Main migration script that:
- Creates the `shop_product_category` junction table
- Adds all product attributes directly to `shop_products` table
- Creates necessary indexes for performance
- Adds a trigger for slug uniqueness within each shop
- Makes the `price` column required

### 2. `make_shop_products_autonomous.py`
Alembic migration file for the same changes. Use this if you're using Alembic for migrations.

### 3. `migrate_shop_products_data.sql`
Data migration script to copy existing product data from `products` table to `shop_products` table.

### 4. `rollback_shop_products_autonomous.sql`
Rollback script to undo the structural changes (WARNING: will lose autonomous data).

## Migration Process

### Option A: Using Raw SQL

1. **Backup your database first!**
   ```sql
   pg_dump your_database > backup_before_migration.sql
   ```

2. **Run the structure migration:**
   ```sql
   \i migrations/update_shop_products_autonomous.sql
   ```

3. **If you have existing data to migrate:**
   ```sql
   \i migrations/migrate_shop_products_data.sql
   ```

### Option B: Using Alembic

1. **Backup your database first!**

2. **Copy the Alembic migration file to your versions directory:**
   ```bash
   cp make_shop_products_autonomous.py mundo_auto/migrations/versions/
   ```

3. **Update the revision ID in the file:**
   - Replace `<previous_revision_id>` with your actual previous revision ID

4. **Run the migration:**
   ```bash
   alembic upgrade head
   ```

5. **If you have existing data to migrate:**
   ```sql
   \i migrations/migrate_shop_products_data.sql
   ```

## New Table Structure

After migration, `shop_products` will have these columns:

### Original Columns (modified)
- `id` - UUID primary key
- `shop_id` - Reference to shop (unchanged)
- `stock_quantity` - Product stock (unchanged)
- `price` - Now required, shop-specific price
- `sale_price` - Shop-specific sale price
- `sku` - Shop-specific SKU
- `is_active` - Whether product is active (unchanged)
- `created_at`, `updated_at` - Timestamps (unchanged)

### New Product Columns
- `name` - Product name (required)
- `slug` - Product slug (unique within shop)
- `description` - Product description
- `technical_details` - Technical specifications
- `oe_number` - Original Equipment number
- `brand` - Product brand
- `manufacturer` - Product manufacturer
- `model` - Vehicle model compatibility
- `manufacturer_year` - Vehicle year compatibility
- `compatible_vehicles` - Array of compatible vehicles
- `weight` - Product weight in kg
- `dimensions` - Product dimensions (LxWxH in cm)
- `image` - Base64 encoded image
- `is_featured` - Whether shop features this product
- `is_on_sale` - Whether shop has this product on sale

### New Junction Table: `shop_product_category`
- `shop_product_id` - Reference to shop_product
- `category_id` - Reference to category
- Primary key on both columns

## Important Notes

1. **Slug Uniqueness**: Slugs are only unique within each shop, not globally
2. **Price Required**: The `price` column is now required for all shop products
3. **Category Relationships**: Products can belong to multiple categories via the junction table
4. **Data Migration**: The data migration script preserves existing relationships
5. **Backup First**: Always backup your database before running migrations

## Verification Queries

After migration, run these queries to verify everything worked correctly:

```sql
-- Check table structure
\d shop_products
\d shop_product_category

-- Verify data integrity
SELECT COUNT(*) FROM shop_products WHERE name IS NULL;
SELECT COUNT(*) FROM shop_products WHERE price IS NULL;

-- Check for slug uniqueness within shops
SELECT shop_id, slug, COUNT(*) 
FROM shop_products 
GROUP BY shop_id, slug 
HAVING COUNT(*) > 1;

-- Verify category relationships
SELECT COUNT(*) FROM shop_product_category;
```

## Rollback

If you need to rollback the changes:

```sql
\i migrations/rollback_shop_products_autonomous.sql
```

**WARNING**: Rollback will remove all the autonomous product data you've added!

## Support

If you encounter issues during migration:
1. Check the PostgreSQL logs for error details
2. Verify you have sufficient permissions
3. Ensure you have enough disk space for the new columns and indexes
4. Test the migration on a copy of your database first
