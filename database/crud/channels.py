# ========================= Импорт библиотек ========================= #
from sqlalchemy import select
from typing import List
import logging

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
    logger.debug(f"➡️ Запрос на создание канала: id={channel_id}, name={channel_name}, user={user_id}")
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Проверяем, существует ли уже канал
                existing = await session.scalar(select(ChannelORM).where(ChannelORM.channel_id == channel_id))
                if existing:
                    logger.warning(f"⚠️ Канал {channel_id} уже существует, пропуск добавления.")
                    return

                channel = ChannelORM(
                    channel_id=channel_id,
                    channel_name=channel_name,
                    owner_id=user_id
                )
                session.add(channel)
                await session.commit()

                logger.info(f"✅ Канал добавлен: {channel_name} ({channel_id}) пользователем {user_id}")

    except Exception as e:
        logger.exception(f"❌ Ошибка при создании канала {channel_id} ({channel_name}): {e}")


# ========================= Получение всех каналов ========================= #
async def get_channels() -> List[ChannelORM]:
    """
    Возвращает все каналы из базы данных.
    """
    logger.debug("📡 Получение списка всех каналов.")
    try:
        async with AsyncSessionLocal() as session:
            result = await session.scalars(select(ChannelORM))
            channels = result.all()
            logger.debug(f"Найдено {len(channels)} каналов в базе.")
            return channels
    except Exception as e:
        logger.exception(f"Ошибка при получении списка каналов: {e}")
        return []
