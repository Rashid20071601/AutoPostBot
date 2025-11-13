# ========================= Импорт библиотек ========================= #
import logging
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram_dialog import DialogManager, StartMode

from lexicon.lexicon import LEXICON_RU
from keyboards import keyboard_utils
from database.crud.users import create_user, user_exists
from database.crud.channels import create_channel
from states.states import MailingCreation, ChannelAdding

# ========================= Инициализация ========================= #
logger = logging.getLogger(__name__)
router = Router()


# ========================= /start и /help ========================= #
async def welcome_handler(message: Message) -> None:
    """
    /start — приветствие пользователя и добавление в БД при первом запуске.
    """
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    try:
        if not await user_exists(user_id=user_id):
            await create_user(user_id=user_id, first_name=first_name, last_name=last_name)
            logger.info(f"Новый пользователь зарегистрирован: id={user_id}, name={first_name or ''} {last_name or ''}")
    except Exception as e:
        logger.exception(f"Ошибка регистрации пользователя {user_id}: {e}")
        await message.answer(LEXICON_RU["unexpected_error"])
        return

    await message.answer(LEXICON_RU["welcome"], reply_markup=keyboard_utils.main_kb())
    logger.debug(f"[Start] Пользователь {user_id} открыл главное меню.")


async def send_help(target) -> None:
    """Отправка справочного сообщения пользователю."""
    await target.answer(LEXICON_RU["help"])


async def help_message(message: Message) -> None:
    """Обработка команды /help."""
    await send_help(message)
    logger.debug(f"[Help] Пользователь {message.from_user.id} вызвал /help")


async def help_callback(call: CallbackQuery) -> None:
    """Обработка нажатия на кнопку 'Помощь'."""
    await send_help(call.message)
    await call.answer()
    logger.debug(f"[Help] Пользователь {call.from_user.id} открыл справку через кнопку.")


# ========================= Добавление канала ========================= #
async def prompt_channel_name(call: CallbackQuery, state: FSMContext) -> None:
    """Запрашивает у пользователя имя нового канала."""
    await call.message.edit_text(LEXICON_RU["add_channel_name"])
    await state.set_state(ChannelAdding.channel_name)
    await call.answer()
    logger.debug(f"[Channel] Пользователь {call.from_user.id} начал добавление канала.")


async def receive_channel_name(message: Message, state: FSMContext) -> None:
    """Сохраняет имя канала и переходит к запросу ID."""
    await state.update_data(channel_name=message.text)
    await message.answer(LEXICON_RU["add_channel_id"])
    await state.set_state(ChannelAdding.channel_id)
    logger.debug(f"[Channel] {message.from_user.id} указал имя канала: {message.text}")


async def receive_channel_id_and_create(message: Message, state: FSMContext) -> None:
    """Получает ID канала и создаёт запись в БД."""
    user_id = message.from_user.id
    data = await state.get_data()
    channel_name = data.get("channel_name")

    try:
        channel_id = int(message.text)
    except ValueError:
        await message.answer(LEXICON_RU["channel_id_error"])
        logger.warning(f"[Channel] user={user_id} ввёл некорректный ID: {message.text}")
        return

    try:
        await create_channel(channel_id=channel_id, channel_name=channel_name, user_id=user_id)
        await message.answer(LEXICON_RU["channel_added"])
        logger.info(f"[Channel] user={user_id} добавил канал {channel_name} ({channel_id})")
    except Exception as e:
        logger.exception(f"Ошибка при создании канала для user={user_id}: {e}")
        await message.answer(LEXICON_RU["unexpected_error"])
    finally:
        await state.clear()


# ========================= Создание рассылки ========================= #
async def start_mailing_creation(callback: CallbackQuery, state: FSMContext, dialog_manager: DialogManager) -> None:
    """Начало создания рассылки — запрос текста."""
    user_id = callback.from_user.id
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON_RU["get_mailing"],
        reply_markup=keyboard_utils.back_to_menu_kb(),
    )
    await dialog_manager.start(
        MailingCreation.text,
        mode=StartMode.RESET_STACK
    )
    logger.debug(f"[Mailing] Пользователь {user_id} начал создание рассылки.")


# ========================= Регистрация хэндлеров ========================= #
# /start и /help
router.message.register(welcome_handler, Command("start"), StateFilter(default_state))
router.message.register(help_message, Command("help"), StateFilter(default_state))
router.callback_query.register(help_callback, F.data == "help", StateFilter(default_state))

# Добавление канала
router.callback_query.register(prompt_channel_name, F.data == "add_channel")
router.message.register(receive_channel_name, StateFilter(ChannelAdding.channel_name))
router.message.register(receive_channel_id_and_create, StateFilter(ChannelAdding.channel_id))

# Создание рассылки
router.callback_query.register(start_mailing_creation, F.data == "create_post", StateFilter(default_state))
