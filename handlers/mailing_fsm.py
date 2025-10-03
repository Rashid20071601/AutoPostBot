# ========================= Импорт библиотек ========================= #
from aiogram import Bot, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram_dialog import DialogManager, StartMode
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramNotFound
import logging

from lexicon.lexicon import LEXICON_RU
from keyboards import keyboard_utils
from database.db import add_mailing
from states.states import MailingState


# ========================= Инициализация логирования и роутера ========================= #
logger = logging.getLogger(__name__)
router = Router()


# ========================= Хендлеры приветствия и помощи ========================= #
async def welcome_handler(message: Message) -> None:
    await message.answer(
        text=LEXICON_RU['welcome'],
        reply_markup=keyboard_utils.main_kb(),
    )


async def send_help(target) -> None:
    await target.answer(
        text=LEXICON_RU['help'],
        parse_mode="Markdown"
    )

async def help_message(message: Message) -> None:
    await send_help(message)

async def help_callback(call: CallbackQuery) -> None:
    await send_help(call.message)
    await call.answer()


# ========================= Хендлеры создания поста ========================= #
async def start_mailing_creation(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=LEXICON_RU['get_mailing'],
        reply_markup=keyboard_utils.back_to_menu_kb(),
    )

    await state.set_state(MailingState.text)
    await callback.answer()


async def set_mailing_text(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await state.update_data(text=message.text)
    await dialog_manager.start(MailingState.date, mode=StartMode.RESET_STACK)


async def set_mailing_channel(message: Message, state: FSMContext, bot: Bot):
    """
    Устанавливает канал для рассылки и создает рассылку на основе данных из состояния.

    Args:
        message: Сообщение с ID канала.
        state: Контекст FSM для получения данных.
        bot: Экземпляр бота для взаимодействия с Telegram API.

    Raises:
        ValueError: Если ID канала не является числом.
        TelegramForbiddenError: Если бот не имеет прав в канале.
    """

    try:
        chanel_id = int(message.text)
    except ValueError:
        logger.error(
            "Invalid channel ID format",
            extra={
                "user_id": message.from_user.id,
                "input_text": message.text,
            }
        )
        await message.answer(
            text=LEXICON_RU['channel_id_error'],

        )
        await state.clear()
        return

    try:
        chat_memeber = await bot.get_chat_member(chanel_id, bot.id)
        if chat_memeber.status not in ("administrator", "creator"):
            raise TelegramForbiddenError("Bot is not an admin in the channel")
        test_msg = await bot.send_message(chanel_id, LEXICON_RU["test_message"])
        await bot.delete_message(chanel_id, test_msg.message_id)

    except (TelegramBadRequest, TelegramForbiddenError, TelegramNotFound) as e:
        logger.error(
            "Failed to send or delete test message",
            extra={
                "user_id": message.from_user.id,
                "chanel_id": chanel_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
            }
        )
        await message.answer(
            text=LEXICON_RU['mailing_message_error'],

        )
        await state.clear()
        return

    except Exception:
        logger.exception(
            "Unexpected error in set_mailing_channel",
            extra={
                "user_id": message.from_user.id,
                "chanel_id": chanel_id,
                "dialog_data": await state.get_data(),
            }
        )
        await message.answer(
            text=LEXICON_RU['unexpected_error'],

        )
        await state.clear()
        return

    data = await state.get_data()
    await add_mailing(data["text"], data["hour"], data["minute"], chanel_id)
    await message.answer(
        text=LEXICON_RU['mailing_created'],
    )
    await state.clear()



# ========================= Регистрация хэндлеров ========================= #
# /start
router.message.register(welcome_handler, Command(commands="start"), StateFilter(default_state))

# /help
router.message.register(help_message, Command(commands="help"), StateFilter(default_state))

# Запрос помощи
router.callback_query.register(help_callback, F.data == "help", StateFilter(default_state))

# Запрос текста поста
router.callback_query.register(start_mailing_creation, F.data == "create_post", StateFilter(default_state))

# Запрос часов
router.message.register(set_mailing_text, StateFilter(MailingState.text))