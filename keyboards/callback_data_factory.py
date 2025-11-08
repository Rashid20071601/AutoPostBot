# ========================= Импорт библиотек ========================= #
from aiogram.filters.callback_data import CallbackData
from typing import List, Dict, Any
import logging

from database.crud.channels import get_channels


# ========================= Инициализация логгера ========================= #
logger = logging.getLogger(__name__)


# ========================= Callback Factory ========================= #
class ChannelSelectCallback(CallbackData, prefix="channel"):
    """
    CallbackData для кнопок выбора каналов.
    Используется в диалогах рассылки (handlers/mailing_datetime.py).
    """
    channel_id: int


# ========================= Функции получения каналов ========================= #
async def get_user_channels(user_id: int) -> List[Dict[str, Any]]:
    """
    Возвращает список каналов, принадлежащих пользователю.

    Формат:
        [
            {"id": <int>, "title": <str>},
            ...
        ]

    Используется в aiogram-dialog (Select widget), чтобы
    отобразить список доступных каналов при планировании рассылки.
    """
    try:
        channels = await get_channels()
        user_channels = [
            {"id": ch.channel_id, "title": ch.channel_name}
            for ch in channels
            if ch.owner_id == user_id
        ]

        if not user_channels:
            logger.warning(f"[Channels] У пользователя {user_id} нет добавленных каналов.")
        else:
            logger.debug(f"[Channels] Пользователь {user_id}: найдено {len(user_channels)} каналов")

        return user_channels

    except Exception as e:
        logger.exception(f"❌ Ошибка при получении каналов пользователя {user_id}: {e}")
        return []
