from app.db.session import SessionLocal
from sqlalchemy import text

def check_shop_products_schema():
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'shop_products' 
            ORDER BY ordinal_position;
        """))
        
        print("shop_products table schema:")
        print("-" * 40)
        for row in result.fetchall():
            nullable = "NULL" if row[2] == "YES" else "NOT NULL"
            print(f"{row[0]}: {row[1]} ({nullable})")
    finally:
        db.close()

if __name__ == "__main__":
    check_shop_products_schema()