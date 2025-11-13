# ========================= Импорт библиотек ========================= #
import logging
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramNotFound
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Calendar, Select, Group
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row

from lexicon.lexicon import LEXICON_RU
from states.states import MailingCreation
from database.crud.mailings import add_mailing
from keyboards.callback_data_factory import get_user_channels, ChannelSelectCallback
from keyboards.keyboard_utils import main_kb


# ========================= Настройка логгера ========================= #
logger = logging.getLogger(__name__)


# ========================= Новые шаги для текста и изображения ========================= #
async def on_text_received(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    """Сохраняем текст рассылки и переходим к шагу добавления изображения."""
    user_id = message.from_user.id
    text = (message.text or "").strip()

    if not text:
        await message.answer(LEXICON_RU["text_error"])
        return

    dialog_manager.dialog_data["text"] = text
    logger.debug(f"[MailingDialog] user={user_id} ввёл текст рассылки ({len(text)} символов).")
    await dialog_manager.next()

async def on_choose_add_image(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    """Переход к шагу загрузки изображения."""
    dialog_manager.dialog_data["add_image"] = True
    await dialog_manager.next()

async def on_skip_image(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    """Пропустить добавление изображения."""
    dialog_manager.dialog_data["add_image"] = False
    await dialog_manager.switch_to(MailingCreation.scheduled_date)
    logger.debug(f"[MailingDialog] user={callback.from_user.id} пропустил изображение.")

async def on_image_received(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    """Получаем изображение рассылки и переходим к выбору даты."""
    user_id = message.from_user.id
    if not message.photo:
        await message.answer(LEXICON_RU["image_error"])
        return

    image_file_id = message.photo[-1].file_id
    dialog_manager.dialog_data["image_file_id"] = image_file_id
    logger.debug(f"[MailingDialog] user={user_id} отправил изображение (file_id={image_file_id}).")
    await dialog_manager.next()


# ========================= Обработчики выбора ========================= #
async def on_date_selected(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Сохраняет дату публикации и переходит к выбору часа."""
    dialog_manager.dialog_data["scheduled_date"] = item_id
    logger.debug(f"[MailingDialog] user={callback.from_user.id} выбрал дату {item_id}")
    await dialog_manager.next()


async def on_hour_selected(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Сохраняет час публикации и переходит к выбору минут."""
    dialog_manager.dialog_data["hour"] = int(item_id)
    logger.debug(f"[MailingDialog] user={callback.from_user.id} выбрал час {item_id}")
    await dialog_manager.next()


async def on_minute_selected(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Сохраняет минуты публикации и переходит к выбору канала."""
    dialog_manager.dialog_data["minute"] = int(item_id)
    logger.debug(f"[MailingDialog] user={callback.from_user.id} выбрал минуты {item_id}")
    await dialog_manager.next()


# ========================= Получение каналов пользователя ========================= #
async def get_channels(dialog_manager: DialogManager, event_from_user, **kwargs) -> dict:
    """
    Возвращает список каналов пользователя для отображения в Select.
    """
    user_id = event_from_user.id
    channels = await get_user_channels(user_id=user_id)

    items = [
        {"id": ChannelSelectCallback(channel_id=ch["id"]).pack(), "title": ch["title"]}
        for ch in channels
    ]

    logger.info(f"[MailingDialog] user={user_id} — найдено {len(items)} каналов")
    return {"channels": items}


# ========================= Проверка канала и создание рассылки ========================= #
async def on_channel_selected(
    callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str
):
    """Проверяет права бота и создаёт запись о рассылке в базе данных."""
    user_id = callback.from_user.id
    channel_data = ChannelSelectCallback.unpack(item_id)
    channel_id = channel_data.channel_id
    dialog_manager.dialog_data["channel"] = channel_id

    logger.debug(f"[MailingDialog] user={user_id} выбрал канал {channel_id}, проверяем доступ...")

    # --- Проверка прав бота в канале --- #
    try:
        chat_member = await callback.bot.get_chat_member(channel_id, callback.bot.id)
        if chat_member.status not in ("administrator", "creator"):
            raise TelegramForbiddenError("Bot is not an admin in the channel")

        # Проверка возможности публикации
        test_msg = await callback.bot.send_message(channel_id, LEXICON_RU["test_message"])
        await callback.bot.delete_message(channel_id, test_msg.message_id)
        logger.debug(f"[MailingDialog] Тестовое сообщение успешно отправлено в канал {channel_id}")

    except (TelegramBadRequest, TelegramForbiddenError, TelegramNotFound) as e:
        logger.warning(f"[MailingDialog] Нет доступа к каналу {channel_id} ({type(e).__name__}): {e}")
        await callback.message.answer(LEXICON_RU["mailing_message_error"])
        return
    except Exception as e:
        logger.exception(f"[MailingDialog] Неизвестная ошибка при проверке канала {channel_id}: {e}")
        await callback.message.answer(LEXICON_RU["unexpected_error"])
        return

    # --- Извлечение данных рассылки --- #
    data = dialog_manager.dialog_data
    text = data.get("text")
    image_file_id = data.get("image_file_id")
    scheduled_date = data.get("scheduled_date")
    hour = data.get("hour")
    minute = data.get("minute")

    logger.info(
        f"[MailingDialog] Создаём рассылку user={user_id}: "
        f"дата={scheduled_date}, время={hour}:{minute:02d}, канал={channel_id}"
    )

    # --- Создание записи в БД --- #
    try:
        await add_mailing(
            text=text,
            image_file_id=image_file_id,
            scheduled_date=scheduled_date,
            hour=hour,
            minute=minute,
            channel_id=channel_id,
        )
        logger.info(f"[MailingDialog] Рассылка создана успешно user={user_id}, channel={channel_id}")
    except Exception as e:
        logger.exception(f"[MailingDialog] Ошибка при добавлении рассылки: {e}")
        await callback.message.answer(LEXICON_RU["unexpected_error"])
        return

    # --- Завершение диалога и возврат --- #
    try:
        dialog_manager.dialog_data.clear()
        await dialog_manager.done()
        logger.debug(f"[MailingDialog] Диалог завершён для user={user_id}")
    except Exception as e:
        logger.warning(f"[MailingDialog] Ошибка при завершении диалога: {e}")

    # FSM очищаем мягко — без жёсткой пересборки
    try:
        state = FSMContext(dialog_manager.event.bot.dispatcher.storage,
                           dialog_manager.event.bot.dispatcher.fsm_key_builder(
                               bot_id=dialog_manager.event.bot.id,
                               user_id=callback.from_user.id,
                               chat_id=callback.message.chat.id,
                           ))
        await state.clear()
        logger.debug(f"[MailingDialog] FSM очищен для user={user_id}")
    except Exception as e:
        logger.warning(f"[MailingDialog] Не удалось очистить FSM для user={user_id}: {e}")

    # Возврат в главное меню
    await callback.message.edit_text(
        text=LEXICON_RU["mailing_created"],
        reply_markup=main_kb(),
    )


# ========================= Диалог выбора даты и канала ========================= #
# --- Получение текста ---
text_window = Window(
    Const(LEXICON_RU["get_mailing"]),
    MessageInput(on_text_received, content_types=["text"]),
    state=MailingCreation.text,
)

# --- Выбор — добавить изображение или пропустить ---
choose_image_window = Window(
    Const(LEXICON_RU["ask_about_image"]),
    Row(
        Button(Const(LEXICON_RU["add_image_button"]), id="add_image", on_click=on_choose_add_image),
        Button(Const(LEXICON_RU["skip_image_button"]), id="skip_image", on_click=on_skip_image),
    ),
    state=MailingCreation.ask_image,
)

# --- Получение изображения ---
image_window = Window(
    Const(LEXICON_RU["get_image"]),
    MessageInput(on_image_received, content_types=["photo"]),
    state=MailingCreation.image_file_id,
)

# --- Получение даты ---
date_window = Window(
    Const(LEXICON_RU["select_date"]),
    Calendar(id="cal", on_click=on_date_selected),
    state=MailingCreation.scheduled_date,
)

# --- Получение часа ---
hour_window = Window(
    Const(LEXICON_RU["select_hour"]),
    Group(
        Select(
            id="hours",
            items=[f"{i:02d}" for i in range(24)],
            item_id_getter=lambda x: x,
            text=Format("{item}"),
            on_click=on_hour_selected,
        ),
        width=6,
    ),
    state=MailingCreation.hour,
)

# --- Получение минуты ---
minute_window = Window(
    Const(LEXICON_RU["select_minute"]),
    Group(
        Select(
            id="minutes",
            items=[f"{i:02d}" for i in range(0, 60, 5)],
            item_id_getter=lambda x: x,
            text=Format("{item}"),
            on_click=on_minute_selected,
        ),
        width=6,
    ),
    state=MailingCreation.minute,
)

# --- Выбор канал ---
channel_window = Window(
    Const(LEXICON_RU["select_channel"]),
    Group(
        Select(
            id="channel",
            items="channels",
            item_id_getter=lambda x: x["id"],
            text=Format("{item[title]}"),
            on_click=on_channel_selected,
        ),
        width=1,
    ),
    state=MailingCreation.channel,
    getter=get_channels,
)

# ========================= Диалог рассылки ========================= #
mailing_dialog = Dialog(
    text_window,
    choose_image_window,
    image_window,
    date_window,
    hour_window,
    minute_window,
    channel_window,
)