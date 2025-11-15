import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database.crud.channels import get_channels_for_user, delete_channel
from keyboards.keyboard_utils import channel_manage_kb, back_to_menu_kb

logger = logging.getLogger(__name__)
router = Router()


# ========================= Открытие управления каналами ========================= #
@router.callback_query(F.data == "manage_channel")
async def open_channel_management(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    channels = await get_channels_for_user(user_id=user_id)  # фильтруем по владельцу
    if not channels:
        await call.message.edit_text("📭 У вас нет добавленных каналов.", reply_markup=back_to_menu_kb())
        await state.clear()
        return

    await show_channel_page(call, channels, 0)


# ========================= Отображение конкретного канала ========================= #
async def show_channel_page(call: CallbackQuery, channels, index: int):
    username = call.from_user.full_name
    channel = channels[index]
    total = len(channels)

    msg_text = (
        f"<b>📢 Название:</b> {channel.channel_name}\n"
        f"<b>🆔 ID:</b> {channel.channel_id}\n"
        f"<b>👤 Владелец:</b> {username}\n\n"
        f"<i>Страница {index + 1}/{total}</i>"
    )

    await call.message.edit_text(msg_text, reply_markup=channel_manage_kb(channel.channel_id, index, total))


# ========================= Пагинация ========================= #
@router.callback_query(F.data.startswith("channel_page:"))
async def change_channel_page(call: CallbackQuery, state: FSMContext):
    try:
        _, direction, index_str, total_str = call.data.split(":")
        index = int(index_str)
        total = int(total_str)
        user_id = call.from_user.id

        channels = await get_channels_for_user(user_id)
        if not channels:
            await call.message.edit_text("📭 Каналов нет.", reply_markup=back_to_menu_kb())
            await state.clear()
            return

        if direction == "next":
            index = (index + 1) % total
        elif direction == "prev":
            index = (index - 1 + total) % total

        await show_channel_page(call, channels, index)
        await call.answer()

    except Exception as e:
        logger.exception(f"Ошибка при переключении страницы каналов: {e}")
        await call.answer("❌ Не удалось переключить страницу.")


# ========================= Удаление канала ========================= #
@router.callback_query(F.data.startswith("delete_channel:"))
async def delete_channel_cb(call: CallbackQuery, state: FSMContext):
    try:
        _, channel_id_str, index_str, total_str = call.data.split(":")
        channel_id = int(channel_id_str)
        index = int(index_str)
        user_id = call.from_user.id

        success = await delete_channel(channel_id)
        if not success:
            await call.answer("❌ Не удалось удалить канал.")
            return

        channels = await get_channels_for_user(user_id)
        if not channels:
            await call.message.edit_text("📭 Каналов нет.", reply_markup=back_to_menu_kb())
            await state.clear()
            return

        index = max(0, min(index, len(channels) - 1))
        await show_channel_page(call, channels, index)
        await call.answer("🗑 Канал удалён.")

    except Exception as e:
        logger.exception(f"Ошибка при удалении канала: {e}")
        await call.answer("❌ Ошибка при удалении канала.")
