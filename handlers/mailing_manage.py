# ========================= Импорт библиотек ========================= #
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from database.crud.mailings import (
    get_mailings,
    get_mailing,
    update_mailing,
    delete_mailing,
)
from keyboards.keyboard_utils import back_to_menu_kb, mailing_manage_kb
from states.states import MailingManageState

# ========================= Инициализация ========================= #
logger = logging.getLogger(__name__)
router = Router()


# ========================= Просмотр рассылок ========================= #
async def manage_mailings_callback(call: CallbackQuery) -> None:
    """
    Отображает список всех рассылок пользователя.
    Если рассылок нет — сообщает об этом.
    """
    user_id = call.from_user.id
    try:
        mailings = await get_mailings()

        if not mailings:
            await call.message.edit_text(
                "📭 У вас пока нет созданных рассылок.",
                reply_markup=back_to_menu_kb()
            )
            logger.info(f"[Mailings] Пользователь {user_id} — нет рассылок.")
            return await call.answer()

        # Отображаем только первую рассылку (по UX — список должен быть в InlineList позже)
        for mailing in mailings:
            status = "✅ Активна" if mailing.enabled else "🚫 Отключена"
            scheduled_date = mailing.scheduled_date.strftime("%Y-%m-%d")
            time_str = f"{mailing.hour:02}:{mailing.minute:02}"

            text_preview = mailing.text
            if len(text_preview) > 200:
                text_preview = text_preview[:200] + "..."

            msg_text = (
                f"<b>📨 ID:</b> <code>{mailing.id}</code>\n"
                f"<b>🕒 Время:</b> {time_str} • {scheduled_date}\n"
                f"<b>📢 Канал:</b> <code>{mailing.channel_id}</code>\n"
                f"<b>📄 Текст:</b>\n<i>{text_preview}</i>\n\n"
                f"<b>Статус:</b> {status}"
            )

            await call.message.edit_text(
                text=msg_text,
                reply_markup=mailing_manage_kb(mailing.id, mailing.enabled)
            )

        logger.info(f"[Mailings] Пользователь {user_id} просмотрел {len(mailings)} рассылок.")
        await call.answer()

    except Exception as e:
        logger.exception(f"Ошибка при отображении рассылок пользователя {user_id}: {e}")
        await call.message.answer(
            "⚠️ Не удалось загрузить рассылки. Попробуйте позже.",
            reply_markup=back_to_menu_kb()
        )
        await call.answer()


# ========================= Переключение статуса ========================= #
async def toggle_mailing(call: CallbackQuery) -> None:
    """
    Включает или выключает выбранную рассылку.
    """
    user_id = call.from_user.id
    try:
        mailing_id = int(call.data.split(":")[1])
        mailing = await get_mailing(mailing_id)

        if not mailing:
            await call.answer("🚫 Рассылка не найдена.")
            return

        new_status = not mailing.enabled
        await update_mailing(mailing_id, enabled=new_status)

        status_text = "✅ Активна" if new_status else "🚫 Отключена"
        scheduled_date = mailing.scheduled_date.strftime("%Y-%m-%d")
        time_str = f"{mailing.hour:02}:{mailing.minute:02}"

        msg_text = (
            f"<b>📨 ID:</b> <code>{mailing.id}</code>\n"
            f"<b>🕒 Время:</b> {time_str} • {scheduled_date}\n"
            f"<b>📢 Канал:</b> <code>{mailing.channel_id}</code>\n"
            f"<b>📄 Текст:</b>\n<i>{mailing.text}</i>\n\n"
            f"<b>Статус:</b> {status_text}"
        )

        await call.message.edit_text(
            msg_text,
            reply_markup=mailing_manage_kb(mailing.id, new_status)
        )
        await call.answer("Статус изменён ✅")

        logger.info(f"[Mailing {mailing_id}] Пользователь {user_id} переключил статус → {status_text}")

    except Exception as e:
        logger.exception(f"Ошибка при переключении статуса рассылки: {e}")
        await call.answer("❌ Ошибка при изменении статуса.")


# ========================= Удаление рассылки ========================= #
async def delete_mailing_cb(call: CallbackQuery) -> None:
    """
    Удаляет выбранную рассылку.
    """
    user_id = call.from_user.id
    try:
        mailing_id = int(call.data.split(":")[1])
        await delete_mailing(mailing_id)

        await call.message.edit_text("🗑️ Рассылка удалена.", reply_markup=back_to_menu_kb())
        await call.answer("Удалено ✅")

        logger.info(f"[Mailing {mailing_id}] Пользователь {user_id} удалил рассылку.")

    except Exception as e:
        logger.exception(f"Ошибка при удалении рассылки: {e}")
        await call.answer("❌ Не удалось удалить рассылку.")


# ========================= Изменение текста рассылки ========================= #
async def edit_text_start(call: CallbackQuery, state: FSMContext) -> None:
    """
    Начинает процесс редактирования текста рассылки.
    """
    user_id = call.from_user.id
    try:
        mailing_id = int(call.data.split(":")[1])
        await state.update_data(edit_id=mailing_id)
        await call.message.answer("✏️ Введите новый текст рассылки:", reply_markup=back_to_menu_kb())
        await state.set_state(MailingManageState.edit_text)
        await call.answer()
        logger.debug(f"[Mailing {mailing_id}] Пользователь {user_id} начал редактирование текста.")
    except Exception as e:
        logger.exception(f"Ошибка при запуске редактирования рассылки: {e}")
        await call.answer("❌ Ошибка при редактировании.")


async def edit_text_finish(message: Message, state: FSMContext) -> None:
    """
    Завершает редактирование текста рассылки и сохраняет изменения.
    """
    user_id = message.from_user.id
    try:
        data = await state.get_data()
        mailing_id = data.get("edit_id")

        if not mailing_id:
            await message.answer("⚠️ Не найдена рассылка для редактирования.", reply_markup=back_to_menu_kb())
            return

        new_text = message.text.strip()
        if not new_text:
            await message.answer("⚠️ Текст не может быть пустым. Попробуйте снова.")
            return

        await update_mailing(mailing_id, text=new_text)
        await message.answer("✅ Текст рассылки успешно обновлён.", reply_markup=back_to_menu_kb())
        await state.clear()

        logger.info(f"[Mailing {mailing_id}] Пользователь {user_id} обновил текст рассылки.")

    except Exception as e:
        logger.exception(f"Ошибка при обновлении текста рассылки: {e}")
        await message.answer("❌ Ошибка при обновлении текста.", reply_markup=back_to_menu_kb())
        await state.clear()


# ========================= Регистрация хэндлеров ========================= #
router.callback_query.register(manage_mailings_callback, F.data == "manage_mailings")
router.callback_query.register(toggle_mailing, F.data.startswith("toggle:"))
router.callback_query.register(delete_mailing_cb, F.data.startswith("delete:"))
router.callback_query.register(edit_text_start, F.data.startswith("edit_text:"))
router.message.register(edit_text_finish, StateFilter(MailingManageState.edit_text))
