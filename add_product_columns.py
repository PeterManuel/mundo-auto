from sqlalchemy import create_engine, text

# Create database engine
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/mundo_auto"
engine = create_engine(DATABASE_URL)

# Execute SQL commands
with engine.connect() as connection:
    # Drop alembic_version table if it exists
    connection.execute(text("DROP TABLE IF EXISTS alembic_version;"))
    # Add our new columns
    connection.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS model VARCHAR;"))
    connection.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS manufacturer_year INTEGER;"))
    connection.execute(text("CREATE INDEX IF NOT EXISTS ix_products_model ON products(model);"))
    connection.commit()