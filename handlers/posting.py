# Import libraries
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging

from keyboards import inline
from texts import texts
from config import PostState
from .start import send_welcome


logger = logging.getLogger(__name__)



# Запрос текста поста
async def handle_create_mailing(callback: CallbackQuery, state: FSMContext):
    logger.info("Пользователь {callback.from_user.id} нажал на кнопку 'Создать пост'...")
    await callback.message.answer(
        texts.get_post,
        reply_markup=inline.back_to_menu_kb(),
        parse_mode="HTML"
    )

    await state.set_state(PostState.text)
    await callback.answer()
    logger.info("Пользователь {callback.from_user.id} перешел в режим создания поста!")

# Запрос интервала
async def handle_mailing_text(message: Message, state: FSMContext):
    logger.info("Пользователь {message.from_user.id} ввел текст поста...")
    await state.update_data(text=message.text)
    await message.answer(
        texts.get_interval,
        reply_markup=inline.back_to_menu_kb(),
        parse_mode="HTML"
    )
    await state.set_state(PostState.interval)
    logger.info("Пользователь {message.from_user.id} ввел интервал!")

# Запрос ID группы
async def handle_mailing_interval(message: Message, state: FSMContext):
    try:
        logger.info("Пользователь {message.from_user.id} ввел интервал...")
        interval = int(message.text)
        if interval < 1:
            raise ValueError
        await state.update_data(interval=interval)
        await message.answer(
            texts.get_chanel_id,
            reply_markup=inline.back_to_menu_kb(),
            parse_mode="HTML",
        )
        await state.set_state(PostState.chanel)
        logger.info("Интервал {interval} успешно установлен!")
    except ValueError:
        logger.exception("Пользователь {message.from_user.id} ввел некорректный интервал!")
        await message.answer(
            texts.get_interval_error,
            parse_mode="HTML"
        )
        await state.clear()
        await send_welcome(message=message)
