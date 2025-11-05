# ========================= Импорт библиотек ========================= #
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
import logging

from database.crud.mailings import get_mailings, update_mailing, get_mailing, delete_mailing
from keyboards.keyboard_utils import back_to_menu_kb, mailing_manage_kb
from states.states import MailingManageState


# ========================= Инициализация ========================= #
logger = logging.getLogger(__name__)
router = Router()


# ========================= Просмотр рассылок ========================= #
async def manage_mailings_callback(call: CallbackQuery) -> None:
    """
    Отображает список всех активных и завершённых рассылок пользователя.
    """
    try:
        mailings = await get_mailings()

        if not mailings:
            await call.message.edit_text("📭 Нет активных рассылок.", reply_markup=back_to_menu_kb())
            await call.answer()
            return

        for m in mailings:
            status = "✅ Включена" if m.enabled else "🚫 Отключена"
            scheduled_date = m.scheduled_date.strftime("%Y-%m-%d")
            hour = str(m.hour).zfill(2)
            minute = str(m.minute).zfill(2)

            await call.message.edit_text(
                text=(
                    f"<b>ID:</b> <code>{m.id}</code>\n"
                    f"<b>Текст:</b> <i>{m.text}</i>\n"
                    f"<b>Время:</b> {hour}:{minute} • {scheduled_date}\n"
                    f"<b>Канал:</b> <code>{m.channel_id}</code>\n"
                    f"<b>Статус:</b> {status}"
                ),
                reply_markup=mailing_manage_kb(m.id, m.enabled),
            )

        logger.info(f"Пользователь {call.from_user.id} просмотрел список рассылок ({len(mailings)} шт.)")
        await call.answer()

    except Exception as e:
        logger.exception(f"❌ Ошибка при загрузке рассылок пользователя {call.from_user.id}: {e}")
        await call.message.answer("⚠️ Не удалось загрузить список рассылок.", reply_markup=back_to_menu_kb())
        await call.answer()


# ========================= Переключение статуса ========================= #
async def toggle_mailing(call: CallbackQuery) -> None:
    """
    Включает или выключает выбранную рассылку.
    """
    try:
        mailing_id = int(call.data.split(":")[1])
        mailing = await get_mailing(mailing_id)

        if not mailing:
            await call.answer("Рассылка не найдена.")
            return

        new_status = not mailing.enabled
        await update_mailing(mailing_id, enabled=new_status)

        scheduled_date = mailing.scheduled_date.strftime("%Y-%m-%d")
        hour = str(mailing.hour).zfill(2)
        minute = str(mailing.minute).zfill(2)

        await call.message.edit_text(
            text=(
                f"<b>ID:</b> <code>{mailing.id}</code>\n"
                f"<b>Текст:</b> <i>{mailing.text}</i>\n"
                f"<b>Время:</b> {hour}:{minute} • {scheduled_date}\n"
                f"<b>Канал:</b> <code>{mailing.channel_id}</code>\n"
                f"<b>Статус:</b> {'✅ Включена' if new_status else '🚫 Отключена'}"
            ),
            reply_markup=mailing_manage_kb(mailing.id, new_status)
        )

        await call.answer("Статус изменён ✅")
        logger.info(f"Изменён статус рассылки {mailing_id}: {'ON' if new_status else 'OFF'}")

    except Exception as e:
        logger.exception(f"Ошибка при переключении рассылки: {e}")
        await call.answer("❌ Ошибка при изменении статуса.")


# ========================= Удаление рассылки ========================= #
async def delete_mailing_cb(call: CallbackQuery) -> None:
    """
    Удаляет выбранную рассылку.
    """
    try:
        mailing_id = int(call.data.split(":")[1])
        await delete_mailing(mailing_id)

        await call.message.edit_text("🗑 Рассылка удалена.", reply_markup=back_to_menu_kb())
        await call.answer("Удалено ✅")

        logger.info(f"Рассылка {mailing_id} удалена пользователем {call.from_user.id}")

    except Exception as e:
        logger.exception(f"Ошибка при удалении рассылки: {e}")
        await call.answer("❌ Не удалось удалить рассылку.")


# ========================= Изменение текста рассылки ========================= #
async def edit_text_start(call: CallbackQuery, state: FSMContext) -> None:
    """
    Начинает процесс редактирования текста рассылки.
    """
    try:
        mailing_id = int(call.data.split(":")[1])
        await state.update_data(edit_id=mailing_id)

        await call.message.answer("✏️ Введите новый текст рассылки:", reply_markup=back_to_menu_kb())
        await state.set_state(MailingManageState.edit_text)
        await call.answer()

        logger.debug(f"Пользователь {call.from_user.id} редактирует рассылку {mailing_id}")

    except Exception as e:
        logger.exception(f"Ошибка при начале редактирования: {e}")
        await call.answer("❌ Ошибка при редактировании.")


async def edit_text_finish(message: Message, state: FSMContext) -> None:
    """
    Завершает редактирование текста рассылки.
    """
    try:
        data = await state.get_data()
        mailing_id = data.get("edit_id")

        if not mailing_id:
            await message.answer("⚠️ Не найдена рассылка для редактирования.", reply_markup=back_to_menu_kb())
            return

        await update_mailing(mailing_id, text=message.text)
        await message.answer("✅ Текст рассылки обновлён.", reply_markup=back_to_menu_kb())
        await state.clear()

        logger.info(f"Рассылка {mailing_id} обновлена пользователем {message.from_user.id}")

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
