# ========================= Импорт библиотек ========================= #
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram_dialog import DialogManager, StartMode
import logging

from lexicon.lexicon import LEXICON_RU
from keyboards import keyboard_utils
from database.crud.channels import create_channel
from database.crud.users import create_user, user_exists
from states.states import MailingState, ChannelState


# ========================= Инициализация логирования и роутера ========================= #
logger = logging.getLogger(__name__)
router = Router()


# ========================= Хендлеры приветствия и помощи ========================= #
async def welcome_handler(message: Message) -> None:
    """
    /start — приветствие пользователя.
    При первом запуске — добавление в базу данных.
    """
    user_id = int(message.from_user.id)
    try:
        if not await user_exists(user_id=user_id):
            first_name = message.from_user.first_name
            last_name = message.from_user.last_name
            await create_user(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name
            )
            logger.info(f"Создан новый пользователь: id={user_id}, "
                        f"name={first_name or ''} {last_name or ''}".strip())
    except Exception as e:
        logger.exception(f"Ошибка при регистрации пользователя user_id={user_id}: {e}")
        await message.answer(LEXICON_RU["unexpected_error"])
        return

    logger.debug(f"Пользователь {user_id} вызвал /start")
    await message.answer(
        text=LEXICON_RU['welcome'],
        reply_markup=keyboard_utils.main_kb(),
    )


async def send_help(target) -> None:
    """
    Отправка справочного сообщения пользователю.
    (parse_mode='HTML' установлен глобально)
    """
    await target.answer(text=LEXICON_RU['help'])


async def help_message(message: Message) -> None:
    """Обработка команды /help в чате."""
    logger.debug(f"Пользователь {message.from_user.id} вызвал /help")
    await send_help(message)


async def help_callback(call: CallbackQuery) -> None:
    """Обработка нажатия на кнопку 'Помощь'."""
    logger.debug(f"Пользователь {call.from_user.id} нажал кнопку помощи")
    await send_help(call.message)
    await call.answer()


# ========================= Добавление канала ========================= #
async def prompt_channel_name(call: CallbackQuery, state: FSMContext) -> None:
    """Просим пользователя ввести имя канала."""
    logger.debug(f"Пользователь {call.from_user.id} добавляет новый канал")
    await call.message.edit_text(LEXICON_RU["add_channel_name"])
    await state.set_state(ChannelState.channel_name)
    await call.answer()


async def receive_channel_name(message: Message, state: FSMContext) -> None:
    """Сохраняем имя канала и переходим к запросу ID."""
    await state.update_data(channel_name=message.text)
    logger.debug(f"Сохранено имя канала от {message.from_user.id}: {message.text}")
    await message.answer(LEXICON_RU["add_channel_id"])
    await state.set_state(ChannelState.channel_id)


async def receive_channel_id_and_create(message: Message, state: FSMContext) -> None:
    """Получаем ID канала, создаём запись в БД."""
    data = await state.get_data()
    channel_name = data.get("channel_name")
    user_id = message.from_user.id

    try:
        channel_id = int(message.text)
    except ValueError:
        logger.warning(f"Некорректный ID канала от user={user_id}: {message.text}")
        await message.answer(LEXICON_RU["channel_id_error"])
        return

    logger.info(f"Создание канала '{channel_name}' ({channel_id}) для user={user_id}")
    try:
        await create_channel(channel_id=channel_id, channel_name=channel_name, user_id=user_id)
    except Exception:
        logger.exception(f"Ошибка при создании канала channel_id={channel_id}, user={user_id}")
        await message.answer(LEXICON_RU["unexpected_error"])
        await state.clear()
        return

    await message.answer(LEXICON_RU["channel_added"])
    logger.debug(f"Канал '{channel_name}' ({channel_id}) успешно добавлен пользователем {user_id}")
    await state.clear()


# ========================= Создание рассылки ========================= #
async def start_mailing_creation(callback: CallbackQuery, state: FSMContext):
    """Начало создания рассылки: запрос текста."""
    user_id = callback.from_user.id
    logger.debug(f"Пользователь {user_id} начал создание рассылки")
    await callback.answer()
    await callback.message.edit_text(
        text=LEXICON_RU['get_mailing'],
        reply_markup=keyboard_utils.back_to_menu_kb(),
    )
    await state.set_state(MailingState.text)


async def set_mailing_text(message: Message, state: FSMContext):
    """
    Получает текст рассылки и предлагает пользователю добавить изображение.
    """
    user_id = message.from_user.id
    text = message.text

    if not text:
        logger.warning(f"[Mailing] Пользователь {user_id} отправил пустое сообщение вместо текста.")
        await message.answer(text=LEXICON_RU["text_error"])
        return
    logger.debug(f"Получен текст рассылки от user={user_id}: {text[:50]}...")

    await state.update_data(text=text)
    await message.answer(
        text=LEXICON_RU["ask_about_image"],
        reply_markup=keyboard_utils.add_image_kb()
    )


async def set_mailing_image(callback: CallbackQuery, state: FSMContext):
    """Next time"""
    await callback.answer()
    await callback.message.answer(text=LEXICON_RU["get_image"])
    await state.set_state(MailingState.image_file_id)


async def get_mailing_image(message: Message, state: FSMContext, dialog_manager: DialogManager):
    """Получение изображения рассылки и запуск диалога выбора даты."""
    user_id = message.from_user.id

    if not message.photo:
        logger.warning(f"[Mailing] Пользователь {user_id} не прислал фото при ожидании изображения.")
        await message.answer(text=LEXICON_RU["image_error"])
        return

    image_file_id = message.photo[-1].file_id
    await state.update_data(image_file_id=image_file_id )

    logger.debug(f"[Mailing] Получено изображение от user={user_id}: {image_file_id}")

    logger.debug(f"Переход в диалог выбора даты рассылки для user={user_id}")
    await dialog_manager.start(
        MailingState.scheduled_date,
        mode=StartMode.RESET_STACK,
        data=await state.get_data(),
    )


async def skip_image_and_start_dialog(callback: CallbackQuery, state: FSMContext, dialog_manager: DialogManager):
    """Пользователь пропускает добавление изображения и сразу выбирает дату рассылки."""
    user_id = callback.message.from_user.id
    logger.debug(f"Переход в диалог выбора даты рассылки для user={user_id}")
    await dialog_manager.start(
        MailingState.scheduled_date,
        mode=StartMode.RESET_STACK,
        data=await state.get_data(),
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
router.callback_query.register(set_mailing_image, F.data == "image_add", StateFilter(MailingState.text))
router.message.register(get_mailing_image, F.content_type == "photo", StateFilter(MailingState.image_file_id))
router.callback_query.register(skip_image_and_start_dialog, F.data == "image_skip", StateFilter(MailingState.text))
