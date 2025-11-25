"""
Database migration script to add password reset fields
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine


def add_password_reset_columns():
    """Add password reset columns to users table"""
    try:
        with engine.connect() as connection:
            # Check if columns exist first
            check_columns = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('reset_password_token', 'reset_password_expires')
            """)
            
            existing_columns = connection.execute(check_columns).fetchall()
            existing_column_names = [col[0] for col in existing_columns]
            
            if 'reset_password_token' not in existing_column_names:
                print("Adding reset_password_token column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN reset_password_token VARCHAR"))
                connection.commit()
                print("✅ Added reset_password_token column")
            else:
                print("✅ reset_password_token column already exists")
            
            if 'reset_password_expires' not in existing_column_names:
                print("Adding reset_password_expires column...")
                connection.execute(text("ALTER TABLE users ADD COLUMN reset_password_expires TIMESTAMP"))
                connection.commit()
                print("✅ Added reset_password_expires column")
            else:
                print("✅ reset_password_expires column already exists")
            
            print("\n🎉 Database migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Error adding columns: {str(e)}")


if __name__ == "__main__":
    print("🗄️ Adding password reset columns to users table...")
    add_password_reset_columns()