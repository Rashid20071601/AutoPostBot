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
async def handle_back_to_menu(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Возвращает пользователя в главное меню.
    Очищает FSM-состояние и обновляет сообщение.
    """
    user_id = callback.from_user.id
    logger.debug(f"🔙 Пользователь {user_id} нажал 'Назад в меню'")

    try:
        # Сброс текущего состояния
        await state.clear()

        # Попытка отредактировать текущее сообщение (если есть)
        try:
            await callback.message.edit_text(
                text=LEXICON_RU["welcome"],
                reply_markup=keyboard_utils.main_kb(),
            )
        except Exception as edit_error:
            # Если сообщение уже не редактируемое — просто отправим новое
            logger.debug(f"Не удалось отредактировать сообщение (user={user_id}): {edit_error}")
            await callback.message.answer(
                text=LEXICON_RU["welcome"],
                reply_markup=keyboard_utils.main_kb(),
            )

        await callback.answer()
        logger.info(f"🔁 Пользователь {user_id} успешно возвращён в главное меню")

    except Exception as e:
        logger.exception(f"❌ Ошибка при возврате пользователя {user_id} в главное меню: {e}")
        try:
            await callback.message.answer(LEXICON_RU["unexpected_error"])
        except Exception as inner_e:
            logger.error(f"Не удалось уведомить пользователя об ошибке: {inner_e}")
