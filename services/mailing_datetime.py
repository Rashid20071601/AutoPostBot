from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Calendar, Select, Group
from aiogram_dialog.widgets.text import Const, Format
from aiogram.types import CallbackQuery
import logging

from lexicon.lexicon import LEXICON_RU
from states.states import MailingState


logger = logging.getLogger(__name__)


# ===================== Хэндлеры выбора ===================== #
# Выбор даты
async def on_date_selected(
        callback: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        item_id: str
):
    dialog_manager.dialog_data["date"] = item_id
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
async def get_channels(dialog_manager: DialogManager, **kwargs):
    return {
        "channels": [
            {"id": "-1001234567890", "title": "Не рабочий канал"},
            {"id": "-1003094411124", "title": "Рабочий канал"},
        ]
    }

async def on_channel_selected(
        callback: CallbackQuery,
        widget: Select,
        dialog_manager: DialogManager,
        item_id: str
):
    dialog_manager.dialog_data["chanel"] = int(item_id)
    await dialog_manager.done()
    # await call.message.edit_text(
    #     text=LEXICON_RU[""]
    # )


# ===================== Окна ===================== #
date_window = Window(
    Const(LEXICON_RU["select_date"]),
    Calendar(id="cal", on_click=on_date_selected),
    state=MailingState.date
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