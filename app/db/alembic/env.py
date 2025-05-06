import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic import context

from app.core.config import settings
from app.db.session import Base
from app.models import wallet, transaction, whitelist

from sqlalchemy.ext.asyncio import async_engine_from_config

# Load Alembic configuration
config = context.config

# Load logging configuration from alembic.ini
fileConfig(config.config_file_name)

# Inject DATABASE_URL from FastAPI settings into Alembic config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Metadata used for 'autogenerate' feature (detect model changes)
target_metadata = Base.metadata


# Run migrations without a live database connection (e.g., for generating SQL scripts)
def run_migrations_offline():
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# Run migrations with a live database connection
def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


# Async version of running migrations online (works with asyncpg and async engine)
async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# Entry point — choose offline or online mode based on context
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
