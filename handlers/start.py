# Импорт библиотек
from aiogram.types import Message
from dotenv import load_dotenv
import os

from texts import texts
from keyboards import inline


# --------------- Получение ID админа --------------- #
load_dotenv()
ADMIN_ID = int(os.getenv('ADMIN_ID'))


# ========================= Хендлеры приветствия ========================= #
async def send_welcome(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer(texts.not_admin, parse_mode="HTML")
        return
    elif message.from_user.id == ADMIN_ID:
        await message.answer(
            texts.is_admin,
            reply_markup=inline.admin_main_kb(),
            parse_mode="HTML"
        )
