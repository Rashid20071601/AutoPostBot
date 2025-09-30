from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Calendar, Select, Group
from aiogram_dialog.widgets.text import Const, Format

from lexicon.lexicon import LEXICON_RU
from states.states import MailingState


# ===================== Хэндлеры выбора ===================== #
# Выбор даты
async def on_date_selected(c, widget, manager: DialogManager, date):
    manager.dialog_data["date"] = date
    await manager.next()

# Выбор часа
async def on_hour_selected(c, widget, manager: DialogManager, item_id: str):
    manager.dialog_data["hour"] = int(item_id)
    await manager.next()

# Выбор минуты
async def on_minute_selected(c, widget, manager: DialogManager, item_id: str):
    manager.dialog_data["minute"] = int(item_id)
    await manager.done()


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


# ===================== Диалог ===================== #
mailing_dialog = Dialog(date_window, hour_window, minute_window)