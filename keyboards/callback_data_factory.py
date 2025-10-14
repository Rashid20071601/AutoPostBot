from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
import logging

from database.crud.channels import get_channels


# Классы создания callback_data кнопки.
class ChannelsCallbackFactory(CallbackData, prefix="channels"):
    channel_id: int


# Функции создания кнопки
async def get_user_channels(user_id: int) -> List[dict]:
    """Возвращает список каналов пользователя в формате для aiogram-dialog Select."""
    channels = await get_channels()
    return [
        {"id": ch.channel_id, "title": ch.channel_name} for ch in channels if ch.owner_id == user_id
    ]
