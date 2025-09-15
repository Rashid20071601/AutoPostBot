# Import libraries
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)


logger.debug("Загрузка клавиатур...")

def admin_main_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать рассылку", callback_data="create_post")],
            [InlineKeyboardButton(text="📋 Управление рассылками", callback_data="manage_posts")]
        ]
    )

def back_to_menu_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Вернуться", callback_data="back_to_menu")]
        ]
    )

logger.info("Клавиатуры загружены!")