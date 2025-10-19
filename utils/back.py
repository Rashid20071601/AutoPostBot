from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from lexicon.lexicon import LEXICON_RU
from keyboards import keyboard_utils


logger = logging.getLogger(__name__)
router = Router()



@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    try:
        await state.clear()

        await callback.message.edit_text(
            text=LEXICON_RU['welcome'],
            reply_markup=keyboard_utils.main_kb(),
            parse_mode="HTML"
        )

        await callback.answer()
        logger.info(f"Пользователь {callback.from_user.id} вернулся в главное меню!")

    except Exception as e:
        logger.exception(f"Пользоваетлю {callback.from_user.id} не удалось вернуться в главное меню: {e}")