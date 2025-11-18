from app.db.session import SessionLocal
from sqlalchemy import text

def remove_product_id_column():
    db = SessionLocal()
    try:
        print("Removing product_id column from shop_products table...")
        
        # First, drop any foreign key constraints related to product_id
        print("1. Dropping foreign key constraints...")
        db.execute(text("ALTER TABLE shop_products DROP CONSTRAINT IF EXISTS shop_products_product_id_fkey;"))
        
        # Drop any indexes related to product_id
        print("2. Dropping indexes...")
        db.execute(text("DROP INDEX IF EXISTS idx_shop_products_product_id;"))
        
        # Remove the product_id column
        print("3. Removing product_id column...")
        db.execute(text("ALTER TABLE shop_products DROP COLUMN IF EXISTS product_id;"))
        
        # Add a comment to document this change
        print("4. Adding table comment...")
        db.execute(text("COMMENT ON TABLE shop_products IS 'Autonomous shop products table - no longer dependent on products table';"))
        
        db.commit()
        print("✅ Successfully removed product_id column from shop_products table!")
        
        # Verify the change
        print("\nVerifying the change...")
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'shop_products' AND column_name = 'product_id';
        """))
        
        if result.fetchone() is None:
            print("✅ Confirmed: product_id column has been removed.")
        else:
            print("❌ Warning: product_id column still exists.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    remove_product_id_column()