"""
Initialize database with sample data.
"""
import os
import sys

# Add the current directory to the path so 'app' imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import engine, Base


def main() -> None:
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    main()