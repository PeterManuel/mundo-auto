from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.session import engine

with engine.connect() as conn:
    conn.execute(text('ALTER TABLE products ADD COLUMN IF NOT EXISTS model VARCHAR, ADD COLUMN IF NOT EXISTS manufacturer_year INTEGER;'))
    conn.execute(text('CREATE INDEX IF NOT EXISTS ix_products_model ON products(model);'))
    conn.commit()