# Import
from aiogram.fsm.state import State, StatesGroup


class PostState(StatesGroup):
    text = State()
    period = State()
    chanel = State()