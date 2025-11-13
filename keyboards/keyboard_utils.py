# ========================= Импорт библиотек ========================= #
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging


# ========================= Настройка логгера ========================= #
logger = logging.getLogger(__name__)
logger.debug("🔧 Инициализация клавиатур...")


# ========================= Главное меню ========================= #
def main_kb() -> InlineKeyboardMarkup:
    """
    Главное меню управления рассылками.

    Действия:
    • Создать рассылку
    • Управление рассылками
    • Добавить канал
    • Помощь
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Создать рассылку", callback_data="create_post"),
            ],
            [
                InlineKeyboardButton(text="📋 Управление рассылками", callback_data="manage_mailings"),
            ],
            [
                InlineKeyboardButton(text="📢 Добавить канал", callback_data="add_channel"),
            ],
            [
                InlineKeyboardButton(text="🆘 Помощь", callback_data="help"),
            ],
        ]
    )
    logger.debug("[Keyboard] Главное меню создано успешно")
    return keyboard


# ========================= Управление изображением ========================= #
def image_manage_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура управления уже добавленным изображением:
    • ♻ Заменить
    • ❌ Удалить
    • ➡ Продолжить без изменений
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="♻ Заменить", callback_data="image_change"),
            ],
            [
                InlineKeyboardButton(text="❌ Удалить", callback_data="image_delete"),
            ],
            [
                InlineKeyboardButton(text="➡ Продолжить", callback_data="image_continue"),
            ],
        ]
    )
    logger.debug("[Keyboard] image_manage_kb создана успешно")
    return keyboard


# ========================= Управление рассылками ========================= #
def mailing_manage_kb(mailing_id: int, enabled: bool, index: int, total: int):
    status_btn = InlineKeyboardButton(
        text="🚦 Отключить" if enabled else "🚦 Включить",
        callback_data=f"toggle:{mailing_id}:{index}:{total}"
    )
    edit_btn = InlineKeyboardButton(text="✏ Изменить", callback_data=f"edit_text:{mailing_id}:{index}:{total}")
    delete_btn = InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{mailing_id}:{index}:{total}")

    prev_btn = InlineKeyboardButton(text="◀", callback_data=f"page:prev:{index}:{total}")
    next_btn = InlineKeyboardButton(text="▶", callback_data=f"page:next:{index}:{total}")

    back_btn = InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")

    keyboard = [
        [prev_btn, InlineKeyboardButton(text=f"{index + 1}/{total}", callback_data="noop"), next_btn],
        [status_btn],
        [edit_btn, delete_btn],
        [back_btn],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# ========================= Кнопка "Назад в меню" ========================= #
def back_to_menu_kb() -> InlineKeyboardMarkup:
    """
    Кнопка возврата в главное меню.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Вернуться", callback_data="back_to_menu")]
        ]
    )
    logger.debug("[Keyboard] back_to_menu_kb создана успешно")
    return keyboard


logger.info("✅ Все клавиатуры успешно инициализированы!")
