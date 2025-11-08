# ========================= Импорт библиотек ========================= #
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import logging

from database.connection import get_db_url
from config.config import load_config


# ========================= Настройка конфигурации ========================= #
config = load_config()
logger = logging.getLogger(__name__)


# ========================= Создание движка ========================= #
engine = create_async_engine(
    url=get_db_url(config),
    echo=config.log.level == "DEBUG",  # Включаем SQL-echo только при DEBUG
    pool_pre_ping=True,                # Проверка соединений перед использованием
    pool_size=10,                      # Размер пула подключений
    max_overflow=20,                   # Резервные подключения
    future=True
)

logger.info(f"📦 Подключение к БД установлено ({config.db.name}@{config.db.host}:{config.db.port})")


# ========================= Фабрика сессий ========================= #
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)