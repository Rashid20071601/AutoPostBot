# ========================= Импорт библиотек ========================= #
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from lexicon.lexicon import LEXICON_RU
from keyboards import keyboard_utils


# ========================= Инициализация ========================= #
logger = logging.getLogger(__name__)
router = Router()


# ========================= Обработчик "Назад в меню" ========================= #
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Возвращает пользователя в главное меню и сбрасывает состояние FSM.
    """
    user_id = callback.from_user.id
    try:
        # Очищаем текущее состояние (FSM)
        await state.clear()

        # Возврат в главное меню
        await callback.message.edit_text(
            text=LEXICON_RU["welcome"],
            reply_markup=keyboard_utils.main_kb(),
        )

        await callback.answer()
        logger.info(f"🔙 Пользователь {user_id} вернулся в главное меню")

    except Exception as e:
        logger.exception(f"❌ Ошибка при возврате пользователя {user_id} в главное меню: {e}")
        try:
            await callback.message.answer(LEXICON_RU["unexpected_error"])
        except Exception:
            logger.error("Не удалось отправить сообщение об ошибке пользователю.")
