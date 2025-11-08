# ========================= Импорт библиотек ========================= #
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from config.config import load_config
from database.connection import get_db_url


# ========================= Инициализация логгера и конфигурации ========================= #
logger = logging.getLogger(__name__)
config = load_config()


# ========================= Создание асинхронного движка ========================= #
engine = create_async_engine(
    url=get_db_url(config),
    echo=config.log.level.upper() == "DEBUG",  # Показывать SQL только при DEBUG
    pool_pre_ping=True,                        # Проверяет соединение перед использованием
    pool_size=10,                              # Размер пула соединений
    max_overflow=20,                           # Доп. соединения при пиках нагрузки
    pool_timeout=30,                           # Максимальное ожидание при нехватке соединений
    pool_recycle=1800,                         # Пересоздание соединений каждые 30 минут
    future=True,
)

logger.info(
    f"📦 Подключение к PostgreSQL установлено: "
    f"{config.db.user}@{config.db.host}:{config.db.port}/{config.db.name}"
)


# ========================= Фабрика асинхронных сессий ========================= #
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,  # Не выгружать объекты из сессии после commit()
    class_=AsyncSession,
)


# ========================= Тест подключения к базе данных ========================= #
async def test_db_connection():
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: None)
    logger.info("✅ Проверка подключения к БД прошла успешно")
