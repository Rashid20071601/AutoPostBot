# ========================= Импорт библиотек ========================= #
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

# ========================= Настройка логгера ========================= #
logger = logging.getLogger(__name__)
logger.debug("🔧 Загрузка клавиатур...")


# ========================= Главное меню ========================= #
def main_kb() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру главного меню.
    Содержит действия: создание рассылки, управление, добавление канала и помощь.
    """
    try:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📝 Создать рассылку", callback_data="create_post")],
                [InlineKeyboardButton(text="📋 Управление рассылками", callback_data="manage_mailings")],
                [InlineKeyboardButton(text="📢 Добавить канал", callback_data="add_channel")],
                [InlineKeyboardButton(text="🆘 Помощь", callback_data="help")],
            ]
        )
        logger.debug("Главное меню создано успешно.")
        return keyboard

    except Exception as e:
        logger.exception(f"❌ Ошибка при создании клавиатуры main_kb: {e}")
        # возвращаем fallback, чтобы бот не упал
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
        ])


# ========================= Управление рассылками ========================= #
def mailing_manage_kb(mailing_id: int, enabled: bool) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру управления конкретной рассылкой.
    Включает кнопки изменения, включения/отключения и удаления.
    """
    try:
        status_btn_text = "✅ Вкл" if not enabled else "🚫 Выкл"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Изменить текст", callback_data=f"edit_text:{mailing_id}")],
                [
                    InlineKeyboardButton(text=status_btn_text, callback_data=f"toggle:{mailing_id}"),
                    InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete:{mailing_id}")
                ],
                [InlineKeyboardButton(text="🔙 Вернуться", callback_data="back_to_menu")]
            ]
        )
        logger.debug(f"Клавиатура управления рассылкой {mailing_id} создана (enabled={enabled})")
        return keyboard

    except Exception as e:
        logger.exception(f"❌ Ошибка при создании mailing_manage_kb для {mailing_id}: {e}")
        return back_to_menu_kb()


# ========================= Кнопка "Назад в меню" ========================= #
def back_to_menu_kb() -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с одной кнопкой "Назад в меню".
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Вернуться", callback_data="back_to_menu")]
        ]
    )


logger.info("✅ Клавиатуры успешно загружены!")
