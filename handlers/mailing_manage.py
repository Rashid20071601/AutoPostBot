import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
from zoneinfo import ZoneInfo

from database.crud.mailings import get_mailings_for_user
from keyboards.keyboard_utils import back_to_menu_kb
from .mailing_pagination import show_mailing_page

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "manage_mailings")
async def manage_mailings_callback(call: CallbackQuery, state: FSMContext) -> None:
    """
    Отображает активные рассылки (только будущие) с пагинацией.
    """
    user_id = call.from_user.id
    try:
        mailings = await get_mailings_for_user(user_id)
        now = datetime.now(ZoneInfo("Europe/Moscow"))

        # фильтруем только будущие рассылки
        active_mailings = [
            m for m in mailings
            if datetime.combine(
                m.scheduled_date,
                datetime.min.time().replace(hour=m.hour, minute=m.minute, tzinfo=ZoneInfo("Europe/Moscow"))
            ) > now
        ]

        if not active_mailings:
            await call.message.edit_text(
                "📭 Нет предстоящих рассылок.",
                reply_markup=back_to_menu_kb()
            )
            logger.info(f"[Mailings] Пользователь {user_id} — нет активных рассылок.")
            return await call.answer()

        # сохраняем активные рассылки в состояние пользователя
        await state.update_data(active_mailings=[m.id for m in active_mailings])

        # показываем первую страницу
        await show_mailing_page(call, active_mailings, index=0)
        logger.info(f"[Mailings] Пользователь {user_id} просмотрел {len(active_mailings)} активных рассылок.")
        await call.answer()

    except Exception as e:
        logger.exception(f"Ошибка при отображении рассылок пользователя {user_id}: {e}")
        await call.message.answer(
            "⚠️ Не удалось загрузить рассылки. Попробуйте позже.",
            reply_markup=back_to_menu_kb()
        )
        await call.answer()
