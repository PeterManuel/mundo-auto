# Order Items Migration Guide

## Overview
This migration updates the `order_items` table to use `shop_product_id` instead of separate `product_id` and `shop_id` columns, aligning with the autonomous shop products architecture.

## Files
- `migrate_order_items_to_shop_product.sql` - Main migration script
- `rollback_order_items_migration.sql` - Rollback script if needed

## Pre-Migration Steps

1. **Backup your database** before running any migration
2. **Check existing data** to understand the current state:
   ```sql
   SELECT COUNT(*) FROM order_items;
   SELECT DISTINCT product_id, shop_id FROM order_items LIMIT 10;
   ```

## Migration Process

### Step 1: Run the Migration Script
Execute the `migrate_order_items_to_shop_product.sql` script. The script will:
1. Add the new `shop_product_id` column
2. Add foreign key constraint
3. Populate the column by matching existing product/shop combinations with shop_products
4. Provide verification queries

### Step 2: Verify the Migration
After running the script, check for unmatched records:
```sql
SELECT COUNT(*) as unmatched_records 
FROM order_items 
WHERE shop_product_id IS NULL;
```

### Step 3: Handle Unmatched Records (if any)
If there are unmatched records, you'll need to:
1. Create corresponding shop_products for those combinations, OR
2. Manually map them to existing shop_products, OR
3. Delete orphaned order_items (use caution)

### Step 4: Finalize the Migration
Once all records have `shop_product_id` values, uncomment and run:
```sql
ALTER TABLE order_items ALTER COLUMN shop_product_id SET NOT NULL;
```

### Step 5: Clean Up Old Columns
After thorough testing, uncomment and run:
```sql
ALTER TABLE order_items DROP CONSTRAINT IF EXISTS fk_order_items_product_id;
ALTER TABLE order_items DROP CONSTRAINT IF EXISTS fk_order_items_shop_id;
ALTER TABLE order_items DROP COLUMN product_id;
ALTER TABLE order_items DROP COLUMN shop_id;
```

## Post-Migration Testing

1. Test order creation through the API
2. Verify order retrieval works correctly
3. Check that order items display proper product and shop information
4. Ensure cart-to-order conversion works

## Troubleshooting

### Issue: Unmatched Records
**Solution**: These occur when order_items reference product/shop combinations that don't exist in shop_products. You'll need to either create the missing shop_products or map to existing ones.

### Issue: Foreign Key Violations
**Solution**: Ensure all shop_product_id values reference valid shop_products before setting NOT NULL constraint.

## Rollback
If you need to rollback, use the `rollback_order_items_migration.sql` script, but note that this is complex due to the architectural change from centralized products to autonomous shop products.