from datetime import date
from sqlalchemy import select, update, delete
from typing import List, Optional
import logging

from database.base import AsyncSessionLocal
from database.models import ChannelORM

logger = logging.getLogger(__name__)


async def create_channel(
        channel_id: int,
        channel_name: str,
        user_id: int
        ) -> None:
    """Создать канал и привязать к пользователю."""
    logger.debug(f"Входные данные channel_id={channel_id}, channel_name={channel_name}, user_id={user_id}")
    async with AsyncSessionLocal() as session:
        async with session.begin():
            ch = ChannelORM(
                channel_id=channel_id,
                channel_name=channel_name,
                owner_id=user_id
            )
            session.add(ch)
            await session.commit()
        logger.info(f"Канал добавлен: {channel_name} {channel_id} пользователем {user_id}")


async def get_channels() -> List[ChannelORM]:
    """Вернуть все каналы."""
    logger.debug("Получение всех каналов")
    async with AsyncSessionLocal() as session:
        res = await session.scalars(select(ChannelORM))
        channels = res.all()
    logger.debug(f"Найдено {len(channels)} каналов")
    return channels