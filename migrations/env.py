"""
Alembic configuration file for database migrations.
"""

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config.settings import settings
from app.db.session import Base
from app.models.user import User
from app.models.product import Product, Category, ProductImage
from app.models.cart import CartItem
from app.models.order import Order, OrderItem, OrderStatus

# Import all models here for Alembic to detect

# This is the Alembic Config object, which provides access to the values within the .ini file.
config = context.config

# Configure sqlalchemy URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URI)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()