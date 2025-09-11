# Import libraries
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from keyboards import inline
from texts import texts
from config import PostState

logger = logging.getLogger(__name__)



async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    logger.info("Пользователь {callback.from_user.id} нажал на кнопку 'Назад'...")
    await state.clear()

    await callback.message.edit_text(
        texts.send_welcome,
        reply_markup=inline.admin_main_kb(),
        parse_mode="HTML"
    )

    await callback.answer()
    logger.info("Пользователь {callback.from_user.id} вернулся в главное меню!")


async def create_post(callback: CallbackQuery, state: FSMContext):
    logger.info("Пользователь {callback.from_user.id} нажал на кнопку 'Создать пост'...")
    await callback.message.answer(
        texts.create_post_text,
        reply_markup=inline.back_to_menu_kb(),
        parse_mode="HTML"
    )

    await state.set_state(PostState.text)
    await callback.answer()
    logger.info("Пользователь {callback.from_user.id} перешел в режим создания поста!")