from logging.config import fileConfig
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context
from database.models import Base
from database.connection import get_db_url
from config.config import load_config

# Alembic Config object
config = context.config

# Логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Загружаем конфиг
cfg = load_config()

def get_url() -> str:
    # Для asyncpg оставляем +asyncpg
    return get_db_url(cfg)

def run_migrations_offline() -> None:
    """Генерация SQL без подключения к БД (offline)"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online_async():
    """Асинхронные миграции с реальным подключением"""
    connectable = create_async_engine(
        get_url(),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(lambda conn: context.configure(
            connection=conn,
            target_metadata=target_metadata
        ))

        async with connection.begin():
            await connection.run_sync(lambda conn: context.run_migrations())

    await connectable.dispose()

def run_migrations_online() -> None:
    """Запуск асинхронных миграций через asyncio"""
    asyncio.run(run_migrations_online_async())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
