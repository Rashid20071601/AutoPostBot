# ========================= Импорт библиотек ========================= #
import logging
from typing import List
from sqlalchemy import select, delete

from database.base import AsyncSessionLocal
from database.models import ChannelORM


# ========================= Настройка логгера ========================= #
logger = logging.getLogger(__name__)


# ========================= Создание канала ========================= #
async def create_channel(channel_id: int, channel_name: str, user_id: int) -> None:
    """
    Создаёт новый канал и привязывает его к пользователю.
    Если канал с таким ID уже существует — добавление пропускается.
    """
    logger.debug(f"➡️ Попытка добавить канал: {channel_name} ({channel_id}) для user={user_id}")

    async with AsyncSessionLocal() as session:
        try:
            existing = await session.scalar(
                select(ChannelORM).where(ChannelORM.channel_id == channel_id)
            )
            if existing:
                logger.info(f"⚠️ Канал {channel_id} уже существует, пропускаем добавление.")
                return

            session.add(
                ChannelORM(channel_id=channel_id, channel_name=channel_name, owner_id=user_id)
            )
            await session.commit()
            logger.info(f"✅ Канал добавлен: {channel_name} ({channel_id}) для user={user_id}")

        except Exception as e:
            await session.rollback()
            logger.exception(f"❌ Ошибка при создании канала {channel_id}: {e}")


# ========================= Получение всех каналов ========================= #
async def get_channels() -> List[ChannelORM]:
    """
    Возвращает все каналы из базы данных.
    """
    logger.debug("📡 Получение списка всех каналов")
    async with AsyncSessionLocal() as session:
        try:
            result = await session.scalars(select(ChannelORM))
            channels = result.all()
            logger.debug(f"Найдено каналов: {len(channels)}")
            return channels
        except Exception as e:
            logger.exception(f"Ошибка при получении списка каналов: {e}")
            return []


# ========================= Удаление канала (опционально) ========================= #
async def delete_channel(channel_id: int) -> bool:
    """
    Удаляет канал по его channel_id.
    Возвращает True, если удаление прошло успешно.
    """
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(delete(ChannelORM).where(ChannelORM.channel_id == channel_id))
            await session.commit()
            logger.info(f"🗑 Канал {channel_id} удалён.")
            return True
        except Exception as e:
            await session.rollback()
            logger.exception(f"Ошибка при удалении канала {channel_id}: {e}")
            return False
