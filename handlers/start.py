# Import libraries
from aiogram.types import Message
import logging

from texts import texts
from keyboards import inline

logger = logging.getLogger(__name__)



# ========================= Хендлеры приветствия и помощи ========================= #
async def send_welcome(message: Message):
    logger.info("Пользователь {message.from_user.id} нажал на кнопку '/start'...")
    await message.answer(
        texts.send_welcome,
        reply_markup=inline.admin_main_kb(),
        parse_mode="HTML"
    )
    logger.info("Бот ответил пользователю {message.from_user.id}")


async def send_help(message: Message):
    logger.info("Пользователь {message.from_user.id} нажал на кнопку '/help'")
    await message.answer(texts.help_text, parse_mode="HTML")
    logger.info("Бот ответил пользователю {message.from_user.id}")
