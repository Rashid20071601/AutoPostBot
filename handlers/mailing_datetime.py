from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Calendar, Select, Group
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramNotFound
import logging

from lexicon.lexicon import LEXICON_RU
from states.states import MailingState
from database.crud.mailings import add_mailing
from keyboards.callback_data_factory import get_user_channels, ChannelsCallbackFactory


logger = logging.getLogger(__name__)


# ===================== Хэндлеры выбора ===================== #
# Выбор даты
async def on_date_selected(
        callback: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        item_id: str
):
    dialog_manager.dialog_data["scheduled_date"] = item_id
    await dialog_manager.next()

# Выбор часа
async def on_hour_selected(
        callback: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        item_id: str
):
    dialog_manager.dialog_data["hour"] = int(item_id)
    await dialog_manager.next()

# Выбор минуты
async def on_minute_selected(
        callback: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        item_id: str
):
    dialog_manager.dialog_data["minute"] = int(item_id)
    await dialog_manager.next()

# Выбор канала
async def get_channels(dialog_manager: DialogManager, event_from_user, **kwargs) -> dict:
    user_id = event_from_user.id
    channels = await get_user_channels(user_id=user_id)

    items = [
        {"id": ChannelsCallbackFactory(channel_id=ch["id"]).pack(), "title": ch["title"]}
        for ch in channels
    ]

    result = {"channels": items}
    logger.info(f"Получили список каналов пользователя: {items=}, result={result=}")
    return result

async def on_channel_selected(
        callback: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        item_id: str
):
    data = ChannelsCallbackFactory.unpack(item_id)
    channel_id = data.channel_id
    dialog_manager.dialog_data["channel"] = channel_id

    try:
        chat_member = await callback.bot.get_chat_member(channel_id, callback.bot.id)
        if chat_member.status not in ("administrator", "creator"):
            raise TelegramForbiddenError("Bot is not an admin in the channel")
        test_msg = await callback.bot.send_message(channel_id, LEXICON_RU["test_message"])
        await callback.bot.delete_message(channel_id, test_msg.message_id)

    except (TelegramBadRequest, TelegramForbiddenError, TelegramNotFound) as e:
        logger.error(
            "Failed to send or delete test message",
            extra={
                "user_id": callback.message.from_user.id,
                "channel_id": channel_id,
                "error_type": type(e).__name__,
                "error_message": str(e),
            }
        )
        await callback.message.answer(
            text=LEXICON_RU['mailing_message_error'],
        )
        return

    except Exception as e:
        logger.exception(
            f"Unexpected error: {e}",
            extra={
                "user_id": callback.message.from_user.id,
                "chanel_id": channel_id,
            }
        )
        await callback.message.answer(
            text=LEXICON_RU['unexpected_error'],
        )
        return

    data = dialog_manager.dialog_data
    text = data.get("text") or dialog_manager.start_data.get("text")
    scheduled_date, hour, minute = data.get("scheduled_date"), data.get("hour"), data.get("minute")
    await add_mailing(text=text, scheduled_date=scheduled_date, hour=hour, minute=minute, channel_id=channel_id)
    await callback.message.edit_text(LEXICON_RU["mailing_created"])
    await dialog_manager.done()


# ===================== Окна ===================== #
date_window = Window(
    Const(LEXICON_RU["select_date"]),
    Calendar(id="cal", on_click=on_date_selected),
    state=MailingState.scheduled_date
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
    state=MailingState.hour
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
    state=MailingState.minute
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
        width=1
    ),
    state=MailingState.channel,
    getter=get_channels,
)


# ===================== Диалог ===================== #
mailing_dialog = Dialog(date_window, hour_window, minute_window, channel_window)