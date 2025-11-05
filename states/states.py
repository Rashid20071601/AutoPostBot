# ========================= Импорт библиотек ========================= #
from aiogram.fsm.state import State, StatesGroup


# ========================= Состояния для создания рассылки ========================= #
class MailingState(StatesGroup):
    """
    Состояния FSM при создании новой рассылки.
    Используется в handlers/mailing_fsm.py и mailing_datetime.py
    """
    text = State()              # Ввод текста рассылки
    scheduled_date = State()    # Выбор даты
    hour = State()              # Выбор часа
    minute = State()            # Выбор минут
    channel = State()           # Выбор канала


# ========================= Состояния для добавления канала ========================= #
class ChannelState(StatesGroup):
    """
    Состояния FSM при добавлении нового канала пользователем.
    """
    channel_name = State()      # Ввод названия канала
    channel_id = State()        # Ввод ID канала


# ========================= Состояния для управления рассылками ========================= #
class MailingManageState(StatesGroup):
    """
    Состояния FSM при редактировании или управлении существующими рассылками.
    """
    edit_text = State()         # Изменение текста рассылки
