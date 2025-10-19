from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
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
    return get_db_url(cfg).replace("+asyncpg", "")


def run_migrations_offline() -> None:
    """Генерация SQL без подключения к БД"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Миграции с реальным подключением"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        url=get_url(),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
