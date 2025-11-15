from logging.config import fileConfig
import asyncio

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context

from database.models import Base
from database.connection import get_db_url
from config.config import load_config

config = context.config

# Логи
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Модели
target_metadata = Base.metadata

# Конфиги
cfg = load_config()


def get_url() -> str:
    """Получаем async URL"""
    return get_db_url(cfg)


def run_migrations_offline():
    """Offline режим (генерация SQL без подключения к БД)"""
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
    """Online миграции с async connect"""
    connectable = create_async_engine(
        get_url(),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(lambda sync_conn:
            context.configure(
                connection=sync_conn,
                target_metadata=target_metadata
            )
        )

        async with connection.begin():
            await connection.run_sync(lambda sync_conn: context.run_migrations())

    await connectable.dispose()


def run_migrations_online():
    """Запуск миграций через asyncio"""
    asyncio.run(run_migrations_online_async())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()