# Import
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import inline
from texts import texts
from config import PostState



async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text(
        texts.back_to_menu,
        reply_markup=inline.admin_main_kb(),
        parse_mode="HTML"
    )

    await callback.answer()


async def create_post(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        texts.create_post_text,
        reply_markup=inline.back_to_menu_kb(),
        parse_mode="HTML"
    )

    await state.set_state(PostState.text)
    await callback.answer()