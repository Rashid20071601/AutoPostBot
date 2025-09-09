# Импорт библиотек
from aiogram.types import Message

from texts import texts



async def send_welcome(message: Message):
    await message.answer(texts.send_start)