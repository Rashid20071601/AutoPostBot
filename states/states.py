from aiogram.fsm.state import State, StatesGroup


# --------------- Настройка состояний --------------- #
class MailingState(StatesGroup):
    text = State()
    scheduled_date = State()
    hour = State()
    minute = State()
    channel = State()

class ChannelState(StatesGroup):
    channel_name = State()
    channel_id = State()

class MailingManageState(StatesGroup):
    edit_text = State()
