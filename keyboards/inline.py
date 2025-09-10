from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_main_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать рассылку", callback_data="create_mailing")],
            [InlineKeyboardButton(text="📋 Управление рассылками", callback_data="manage_mailings")]
        ]
    )