import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database.crud.mailings import get_mailing, update_mailing, delete_mailing
from keyboards.keyboard_utils import back_to_menu_kb, mailing_manage_kb
from states.states import MailingManagement

logger = logging.getLogger(__name__)
router = Router()


# ========================= Отображение карточки ========================= #
async def show_mailing_page(call: CallbackQuery, mailings, index: int) -> None:
    """Отображает одну карточку рассылки."""
    mailing = mailings[index]
    total = len(mailings)

    status = "✅ Активна" if mailing.enabled else "🚫 Отключена"
    scheduled_date = mailing.scheduled_date.strftime("%Y-%m-%d")
    time_str = f"{mailing.hour:02}:{mailing.minute:02}"
    text_preview = mailing.text[:200] + "..." if len(mailing.text) > 200 else mailing.text

    msg_text = (
        f"<b>📨 ID:</b> <code>{mailing.id}</code>\n"
        f"<b>🕒 Время:</b> {time_str} • {scheduled_date}\n"
        f"<b>📢 Канал:</b> <code>{mailing.channel_id}</code>\n"
        f"<b>📄 Текст:</b>\n<i>{text_preview}</i>\n\n"
        f"<b>Статус:</b> {status}\n"
        f"<i>Страница {index + 1}/{total}</i>"
    )

    await call.message.edit_text(
        msg_text,
        reply_markup=mailing_manage_kb(mailing.id, mailing.enabled, index, total)
    )


# ========================= Переход между страницами ========================= #
@router.callback_query(F.data.startswith("page:"))
async def change_page(call: CallbackQuery, state: FSMContext) -> None:
    """Переключает страницу пагинации."""
    try:
        _, direction, index_str, total_str = call.data.split(":")
        index = int(index_str)
        total = int(total_str)

        data = await state.get_data()
        mailing_ids = data.get("active_mailings", [])
        if not mailing_ids:
            return await call.answer("⚠️ Список рассылок устарел. Откройте управление заново.")

        mailings = [await get_mailing(mid) for mid in mailing_ids if await get_mailing(mid)]

        if direction == "next":
            index = (index + 1) % total
        elif direction == "prev":
            index = (index - 1 + total) % total

        await show_mailing_page(call, mailings, index)
        await call.answer()

    except Exception as e:
        logger.exception(f"Ошибка при переключении страницы: {e}")
        await call.answer("❌ Не удалось переключить страницу.")


# ========================= Переключение статуса ========================= #
@router.callback_query(F.data.startswith("toggle:"))
async def toggle_mailing(call: CallbackQuery, state: FSMContext) -> None:
    """Включает или выключает выбранную рассылку."""
    try:
        _, mailing_id, index_str, total_str = call.data.split(":")
        mailing_id = int(mailing_id)
        index = int(index_str)

        data = await state.get_data()
        mailing_ids = data.get("active_mailings", [])
        mailings = [await get_mailing(mid) for mid in mailing_ids if await get_mailing(mid)]

        mailing = await get_mailing(mailing_id)
        if not mailing:
            return await call.answer("🚫 Рассылка не найдена.")

        new_status = not mailing.enabled
        await update_mailing(mailing_id, enabled=new_status)

        # Обновляем данные рассылки
        mailings[index] = await get_mailing(mailing_id)
        await show_mailing_page(call, mailings, index)

        await call.answer("Статус изменён ✅")
        logger.info(f"[Mailing {mailing_id}] переключён статус → {new_status}")

    except Exception as e:
        logger.exception(f"Ошибка при переключении статуса: {e}")
        await call.answer("❌ Ошибка при изменении статуса.")


# ========================= Удаление рассылки ========================= #
@router.callback_query(F.data.startswith("delete:"))
async def delete_mailing_cb(call: CallbackQuery, state: FSMContext) -> None:
    """Удаляет рассылку и обновляет список в состоянии."""
    try:
        _, mailing_id, index_str, total_str = call.data.split(":")
        mailing_id = int(mailing_id)
        index = int(index_str)

        data = await state.get_data()
        mailing_ids = data.get("active_mailings", [])

        await delete_mailing(mailing_id)
        mailing_ids = [mid for mid in mailing_ids if mid != mailing_id]

        if not mailing_ids:
            await call.message.edit_text("📭 Нет активных рассылок.", reply_markup=back_to_menu_kb())
            await state.clear()
            return

        await state.update_data(active_mailings=mailing_ids)

        mailings = [await get_mailing(mid) for mid in mailing_ids if await get_mailing(mid)]
        index = max(0, min(index, len(mailings) - 1))

        await show_mailing_page(call, mailings, index)
        await call.answer("🗑 Удалено")

    except Exception as e:
        logger.exception(f"Ошибка при удалении рассылки: {e}")
        await call.answer("❌ Не удалось удалить рассылку.")


# ========================= Изменение текста рассылки ========================= #
@router.callback_query(F.data.startswith("edit_text:"))
async def edit_text_start(call: CallbackQuery, state: FSMContext) -> None:
    """Начало редактирования текста рассылки."""
    try:
        _, mailing_id, index_str, total_str = call.data.split(":")
        mailing_id = int(mailing_id)
        index = int(index_str)
        total = int(total_str)

        await state.update_data(edit_id=mailing_id, index=index, total=total)
        await call.message.answer("✏ Введите новый текст рассылки:", reply_markup=back_to_menu_kb())
        await state.set_state(MailingManagement.edit_text)
        await call.answer()

    except Exception as e:
        logger.exception(f"Ошибка при запуске редактирования: {e}")
        await call.answer("❌ Ошибка при редактировании.")


@router.message(MailingManagement.edit_text)
async def edit_text_finish(message: Message, state: FSMContext) -> None:
    """Сохраняет изменения текста и возвращает на ту же страницу."""
    try:
        data = await state.get_data()
        mailing_id = data.get("edit_id")
        index = data.get("index", 0)
        total = data.get("total", 1)

        new_text = message.text.strip()
        if not new_text:
            await message.answer("⚠️ Текст не может быть пустым.")
            return

        await update_mailing(mailing_id, text=new_text)
        mailing = await get_mailing(mailing_id)

        await message.answer("✅ Текст рассылки обновлён.", reply_markup=back_to_menu_kb())
        await state.clear()

    except Exception as e:
        logger.exception(f"Ошибка при обновлении текста рассылки: {e}")
        await message.answer("❌ Ошибка при обновлении текста.", reply_markup=back_to_menu_kb())
        await state.clear()
