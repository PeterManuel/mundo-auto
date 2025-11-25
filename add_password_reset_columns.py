#!/usr/bin/env python3
"""
Script to add password reset columns to the users table
"""

import sys
import os
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from sqlalchemy import text
from app.db.session import get_db_engine
from app.models.user import User  # Import to ensure table is registered


def add_password_reset_columns():
    """Add password reset columns to users table"""
    engine = get_db_engine()
    
    try:
        with engine.connect() as connection:
            # Check if columns already exist
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('reset_password_token', 'reset_password_expires');
            """))
            
            existing_columns = [row[0] for row in result]
            
            if 'reset_password_token' not in existing_columns:
                print("Adding reset_password_token column...")
                connection.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN reset_password_token VARCHAR;
                """))
                connection.commit()
                print("✓ reset_password_token column added")
            else:
                print("✓ reset_password_token column already exists")
            
            if 'reset_password_expires' not in existing_columns:
                print("Adding reset_password_expires column...")
                connection.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN reset_password_expires TIMESTAMP;
                """))
                connection.commit()
                print("✓ reset_password_expires column added")
            else:
                print("✓ reset_password_expires column already exists")
                
        print("\n✅ Database schema updated successfully!")
        
    except Exception as e:
        print(f"❌ Error updating database schema: {str(e)}")
        return False
        
    return True


if __name__ == "__main__":
    print("🔧 Adding password reset columns to users table...")
    success = add_password_reset_columns()
    if not success:
        sys.exit(1)
    print("\n🎉 Password recovery database setup completed!")