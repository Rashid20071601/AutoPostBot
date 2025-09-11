# Импорт библиотек
from aiogram.types import Message

from texts import texts
from keyboards import inline



# ========================= Хендлеры приветствия ========================= #
async def send_welcome(message: Message):
    await message.answer(
        texts.is_admin,
        reply_markup=inline.admin_main_kb(),
        parse_mode="HTML"
    )

async def send_help(message: Message):
    await message.answer(texts.help_text, parse_mode="HTML")
