# ========================= Импорт библиотек ========================= #
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Calendar, Select, Group
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramNotFound
import logging

from lexicon.lexicon import LEXICON_RU
from states.states import MailingState
from database.crud.mailings import add_mailing
from keyboards.callback_data_factory import get_user_channels, ChannelsCallbackFactory
from keyboards.keyboard_utils import main_kb


# ========================= Настройка логгера ========================= #
logger = logging.getLogger(__name__)


# ========================= Обработчики выбора ========================= #
async def on_date_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """
    Сохраняет выбранную пользователем дату рассылки и
    переводит диалог к выбору часа.
    """
    dialog_manager.dialog_data["scheduled_date"] = item_id
    logger.debug(f"User={callback.from_user.id} выбрал дату: {item_id}")
    await dialog_manager.next()


async def on_hour_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """
    Сохраняет выбранный час и переводит диалог к выбору минут.
    """
    dialog_manager.dialog_data["hour"] = int(item_id)
    logger.debug(f"User={callback.from_user.id} выбрал час: {item_id}")
    await dialog_manager.next()


async def on_minute_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """
    Сохраняет выбранные минуты и переводит диалог к выбору канала.
    """
    dialog_manager.dialog_data["minute"] = int(item_id)
    logger.debug(f"User={callback.from_user.id} выбрал минуты: {item_id}")
    await dialog_manager.next()


async def get_channels(dialog_manager: DialogManager, event_from_user, **kwargs) -> dict:
    """
    Получает список каналов, привязанных к пользователю.
    Возвращает словарь для отображения кнопок в окне выбора канала.
    """
    user_id = event_from_user.id
    channels = await get_user_channels(user_id=user_id)

    items = [
        {"id": ChannelsCallbackFactory(channel_id=ch["id"]).pack(), "title": ch["title"]}
        for ch in channels
    ]
    logger.info(f"Загружено {len(items)} каналов для user={user_id}")
    return {"channels": items}


async def on_channel_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    """
    Проверяет, есть ли у бота права администратора в выбранном канале.
    Создает запись о рассылке в базе данных.
    """
    user_id = callback.from_user.id
    data = ChannelsCallbackFactory.unpack(item_id)
    channel_id = data.channel_id
    dialog_manager.dialog_data["channel"] = channel_id

    logger.debug(f"User={user_id} выбрал канал {channel_id} — проверяем права...")

    try:
        chat_member = await callback.bot.get_chat_member(channel_id, callback.bot.id)
        if chat_member.status not in ("administrator", "creator"):
            raise TelegramForbiddenError("Bot is not an admin in the channel")

        # Проверяем возможность отправки сообщения
        test_msg = await callback.bot.send_message(channel_id, LEXICON_RU["test_message"])
        await callback.bot.delete_message(channel_id, test_msg.message_id)
        logger.debug(f"Тестовое сообщение в канал {channel_id} успешно отправлено и удалено")

    except (TelegramBadRequest, TelegramForbiddenError, TelegramNotFound) as e:
        logger.warning(
            f"Ошибка доступа к каналу {channel_id} для user={user_id}: {type(e).__name__} — {e}"
        )
        await callback.message.answer(LEXICON_RU["mailing_message_error"])
        return

    except Exception as e:
        logger.exception(f"Неизвестная ошибка при проверке канала {channel_id}: {e}")
        await callback.message.answer(LEXICON_RU["unexpected_error"])
        return

    # Получаем данные рассылки из контекста
    data = dialog_manager.dialog_data
    text = data.get("text") or dialog_manager.start_data.get("text")
    scheduled_date = data.get("scheduled_date")
    hour = data.get("hour")
    minute = data.get("minute")

    logger.info(
        f"Создаём рассылку для user={user_id}: "
        f"дата={scheduled_date}, время={hour}:{minute:02d}, канал={channel_id}"
    )

    # Добавляем запись в базу данных
    try:
        await add_mailing(
            text=text,
            scheduled_date=scheduled_date,
            hour=hour,
            minute=minute,
            channel_id=channel_id
        )
        logger.info(f"Рассылка успешно создана для user={user_id} в канал={channel_id}")
    except Exception as e:
        logger.exception(f"Ошибка при добавлении рассылки: {e}")
        await callback.message.answer(LEXICON_RU["unexpected_error"])
        return  # ❗ прекращаем выполнение при ошибке

    # ✅ 1. Завершаем диалог
    dialog_manager.dialog_data.clear()
    await dialog_manager.done()

    # ✅ 2. Очищаем FSM состояние пользователя (чтобы не залипало)
    try:
        state = FSMContext(
            storage=dialog_manager.event.bot.dispatcher.storage,
            key=dialog_manager.event.bot.dispatcher.fsm_key_builder(
                bot_id=dialog_manager.event.bot.id,
                user_id=callback.from_user.id,
                chat_id=callback.message.chat.id,
            )
        )
        await state.clear()
        logger.debug(f"FSM состояние очищено для user={user_id}")
    except Exception as e:
        logger.warning(f"Не удалось очистить FSM состояние для user={user_id}: {e}")

    # ✅ 3. Возвращаем пользователя в главное меню
    await callback.message.edit_text(
        text=LEXICON_RU["mailing_created"],
        reply_markup=main_kb()
    )


# ========================= Окна диалога ========================= #
date_window = Window(
    Const(LEXICON_RU["select_date"]),
    Calendar(id="cal", on_click=on_date_selected),
    state=MailingState.scheduled_date,
)

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
    state=MailingState.hour,
)

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
    state=MailingState.minute,
)

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
    state=MailingState.channel,
    getter=get_channels,
)

# ========================= Диалог рассылки ========================= #
mailing_dialog = Dialog(
    date_window,
    hour_window,
    minute_window,
    channel_window,
)
