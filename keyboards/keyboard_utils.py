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
def add_image_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора — добавить изображение или пропустить шаг.
    Используется после ввода текста рассылки.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖼 Добавить изображение", callback_data="image_add")],
            [InlineKeyboardButton(text="➡ Пропустить", callback_data="image_skip")],
        ]
    )
    logger.debug("[Keyboard] add_image_kb создана успешно")
    return keyboard


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
def mailing_manage_kb(mailing_id: int, enabled: bool) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру управления отдельной рассылкой.

    Кнопки:
    • ✏ Изменить текст
    • ✅ Вкл / 🚫 Выкл
    • 🗑 Удалить
    • 🔙 Вернуться
    """
    status_text = "✅ Вкл" if not enabled else "🚫 Выкл"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✏ Изменить текст",
                    callback_data=f"edit_text:{mailing_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text=status_text,
                    callback_data=f"toggle:{mailing_id}",
                ),
                InlineKeyboardButton(
                    text="🗑 Удалить",
                    callback_data=f"delete:{mailing_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Вернуться",
                    callback_data="back_to_menu",
                ),
            ],
        ]
    )
    logger.debug(f"[Keyboard] mailing_manage_kb создана для mailing_id={mailing_id}, enabled={enabled}")
    return keyboard


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
