# Import libraries
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from keyboards import inline
from texts import texts


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
