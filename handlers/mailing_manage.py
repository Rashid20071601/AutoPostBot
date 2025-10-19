from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from datetime import date

from database.crud.mailings import get_mailings, update_mailing, get_mailing, delete_mailing
from keyboards.keyboard_utils import back_to_menu_kb, mailing_manage_kb
from states.states import MailingManageState


router = Router()


# ========================================== Управление рассылкой ========================================================= #
async def manage_mailings_callback(call: CallbackQuery) -> None:
    mailings = await get_mailings()

    if not mailings:
        await call.message.answer("Нет активных рассылок.", reply_markup=back_to_menu_kb())
        await call.answer()
        return

    for m in mailings:
        status = "Включена" if m.enabled else "Отключена"
        scheduled_date = m.scheduled_date.strftime("%Y-%m-%d")
        hour = m.hour
        minute = m.minute
        await call.message.answer(
            f"ID: <code>{m.id}</code>\n"
            f"Текст: <i>{m.text}</i>\n"
            f"Время: <b>{hour}:{minute}. {scheduled_date}</b>\n"
            f"Канал: <code>{m.channel_id}</code>\n"
            f"Статус: <b>{status}</b>",
            reply_markup=mailing_manage_kb(m.id, m.enabled),
        )
    await call.answer()


async def toggle_mailing(call: CallbackQuery):
    mailing_id = int(call.data.split(":")[1])
    mailing = await get_mailing(mailing_id)

    if mailing:
        new_status = not mailing.enabled
        await update_mailing(mailing_id, enabled=new_status)

        scheduled_date = mailing.scheduled_date.strftime("%Y-%m-%d")
        hour = mailing.hour
        minute = mailing.minute
        await call.answer("Статус изменён!")
        await call.message.edit_text(
            f"ID: <code>{mailing.id}</code>\n"
            f"Текст: <i>{mailing.text}</i>\n"
            f"Время: <b>{hour}:{minute}. {scheduled_date}</b>\n"
            f"Канал: <code>{mailing.channel_id}</code>\n"
            f"Статус: <b>{'Включена' if new_status else 'Отключена'}</b>",
            reply_markup=mailing_manage_kb(mailing.id, new_status)
        )
        await call.answer()
        return


async def delete_mailing_cb(call: CallbackQuery):
    mailing_id = int(call.data.split(":")[1])
    await delete_mailing(mailing_id)
    await call.answer("Удалено!")
    await call.message.edit_text("Рассылка удалена.", reply_markup=back_to_menu_kb())


async def edit_text_start(call: CallbackQuery, state: FSMContext):
    mailing_id = int(call.data.split(":")[1])
    await state.update_data(edit_id=mailing_id)
    await call.message.answer("Введите новый текст рассылки:", reply_markup=back_to_menu_kb())
    await state.set_state(MailingManageState.edit_text)
    await call.answer()


async def edit_text_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    mailing_id = data.get("edit_id")
    await update_mailing(mailing_id, text=message.text)
    await message.answer("Текст рассылки обновлён.", reply_markup=back_to_menu_kb())
    await state.clear()

# ========================================================================================================================= #


router.callback_query.register(manage_mailings_callback, F.data == "manage_mailings")
router.callback_query.register(toggle_mailing, F.data.startswith("toggle:"))
router.callback_query.register(delete_mailing_cb, F.data.startswith("delete:"))
router.callback_query.register(edit_text_start, F.data.startswith("edit_text:"))
router.message.register(edit_text_finish, StateFilter(MailingManageState.edit_text))
