# ========================= Импорт библиотек ========================= #
from aiogram.filters.callback_data import CallbackData
from typing import List, Dict
import logging

from database.crud.channels import get_channels


# ========================= Инициализация логгера ========================= #
logger = logging.getLogger(__name__)


# ========================= Callback Factory ========================= #
class ChannelsCallbackFactory(CallbackData, prefix="channels"):
    """
    CallbackData для кнопок выбора каналов.
    Используется в диалогах рассылки (mailing_datetime.py)
    """
    channel_id: int


# ========================= Функции получения каналов ========================= #
async def get_user_channels(user_id: int) -> List[Dict[str, str]]:
    """
    Возвращает список каналов, принадлежащих пользователю.
    Формат — список словарей: [{"id": <int>, "title": <str>}]
    Используется в aiogram-dialog Select.
    """
    try:
        channels = await get_channels()
        user_channels = [
            {"id": ch.channel_id, "title": ch.channel_name}
            for ch in channels
            if ch.owner_id == user_id
        ]

        logger.debug(f"Пользователь {user_id}: найдено {len(user_channels)} каналов")
        return user_channels

    except Exception as e:
        logger.exception(f"Ошибка при получении каналов пользователя {user_id}: {e}")
        return []
