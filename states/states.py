from aiogram.fsm.state import State, StatesGroup


# --------------- Настройка состояний --------------- #
class MailingState(StatesGroup):
    text = State()
    scheduled_date = State()
    hour = State()
    minute = State()
    channel = State()

class AddChanel(StatesGroup):
    channel_name = State()
    channel_id = State()