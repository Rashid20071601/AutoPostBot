from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
import time

from database.db import get_mailings
from keyboards.keyboard_utils import back_to_menu_kb, mailing_manage_kb


router = Router()


async def manage_mailings_callback(callback: CallbackQuery) -> None:
    mailings = await get_mailings()

    if not mailings:
        await callback.message.answer("Нет активных рассылок.", reply_markup=back_to_menu_kb)
        await callback.answer()
        return

    for m in mailings:
        status = "Включена" if m[5] else "Отключена"
        hour = f"{int(m[2])} ч."
        minute = f"{int(m[3])} мин."

        await callback.message.answer(
            f"ID: <code>{m[0]}</code>\n"
            f"Текст: <i>{m[1]}</i>\n"
            f"Время: <b>{hour} {minute}</b>\n"
            f"Канал: <code>{m[4]}</code>\n"
            f"Статус: <b>{status}</b>",
            reply_markup=mailing_manage_kb(m[0], m[5]),
            parse_mode="HTML"
        )

    await callback.answer()




router.callback_query.register(manage_mailings_callback, F.data == "manage_mailings")