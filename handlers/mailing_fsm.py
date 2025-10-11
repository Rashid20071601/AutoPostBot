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
from database.crud.channels import create_channel
from states.states import MailingState, ChannelState


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


# ========================= Хендлер добавления канала ========================= #
async def prompt_channel_name(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(
        LEXICON_RU["add_channel_name"]
    )
    await state.set_state(ChannelState.channel_name)
    await call.answer()


async def receive_channel_name(message: Message, state: FSMContext) -> None:
    await state.update_data(channel_name=message.text)
    logger.debug(f"Сохранено имя канала: {message.text} для {message.from_user.id}")
    await message.answer(
        LEXICON_RU["add_channel_id"]
    )
    await state.set_state(ChannelState.channel_id)

async def receive_channel_id_and_create(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    channel_name = data.get("channel_name")
    try:
        channel_id = int(message.text)
    except ValueError:
        logger.warning(f"Неверный формат id от user={message.from_user.id}: {message.text}")
        await message.answer(LEXICON_RU["channel_id_error"])
        return

    user_id = message.from_user.id
    logger.debug(f"Создаем канал {channel_name} ({channel_id}) для user={user_id}")

    try:
        await create_channel(channel_id=channel_id, channel_name=channel_name, user_id=user_id)
    except Exception:
        logger.exception(f"Ошибка при создании канала channel_id={channel_id} user={user_id}")
        await message.answer(LEXICON_RU["unexpected_error"])
        await state.clear()
        return

    await message.answer(LEXICON_RU["channel_added"])



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
    await dialog_manager.start(
        MailingState.scheduled_date,
        mode=StartMode.RESET_STACK,
        data=await state.get_data()
        )



# ========================= Регистрация хэндлеров ========================= #
# /start
router.message.register(welcome_handler, Command(commands="start"), StateFilter(default_state))

# /help
router.message.register(help_message, Command(commands="help"), StateFilter(default_state))
router.callback_query.register(help_callback, F.data == "help", StateFilter(default_state))

# Добавление канала
router.callback_query.register(prompt_channel_name, F.data == "add_channel")
router.message.register(receive_channel_name, StateFilter(ChannelState.channel_name))
router.message.register(receive_channel_id_and_create, StateFilter(ChannelState.channel_id))

# Создание рассылки/поста
router.callback_query.register(start_mailing_creation, F.data == "create_post", StateFilter(default_state))
router.message.register(set_mailing_text, StateFilter(MailingState.text))