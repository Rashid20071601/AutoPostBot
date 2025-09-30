# ========================= Импорт библиотек ========================= #
from aiogram import Bot, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram_dialog import DialogManager, StartMode
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
        parse_mode="HTML"
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
        parse_mode="HTML"
    )

    await state.set_state(MailingState.text)
    await callback.answer()


async def set_mailing_text(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await state.update_data(text=message.text)
    await dialog_manager.start(MailingState.date, mode=StartMode.RESET_STACK)


async def set_mailing_time(message: Message, state: FSMContext):
    await message.answer(
        text=LEXICON_RU['get_channel_id'],
        reply_markup=keyboard_utils.back_to_menu_kb(),
        parse_mode="HTML",
    )
    await state.set_state(MailingState.chanel)


async def set_mailing_channel(message: Message, state: FSMContext, bot: Bot):
    try:
        chanel_id = int(message.text)

    except ValueError:
        await message.answer(
            text=LEXICON_RU['channel_id_error'],
            parse_mode="HTML"
        )
        await state.clear()
        await welcome_handler(message=message)

    try:
        test_msg = await bot.send_message(chanel_id, LEXICON_RU['test_message'])
        await bot.delete_message(chanel_id, test_msg.message_id)

    except Exception:
        await message.answer(
            text=LEXICON_RU['mailing_message_error'],
            parse_mode="HTML",
        )
        await state.clear()
        await welcome_handler(message=message)

    data = await state.get_data()
    await add_mailing(data["text"], data["hour"], data["minute"], chanel_id)
    await message.answer(
        text=LEXICON_RU['mailing_created'],
        parse_mode="HTML"
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

# Запрос ID группы
router.message.register(set_mailing_time, StateFilter(MailingState.minute))

# Обработка поста
router.message.register(set_mailing_channel, StateFilter(MailingState.chanel))