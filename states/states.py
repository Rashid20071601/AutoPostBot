# Import libraries
from aiogram.fsm.state import State, StatesGroup
import logging

logger = logging.getLogger(__name__)


logger.debug("Загрузка состояний...")


# --------------- Настройка состояний --------------- #
class MailingState(StatesGroup):
    text = State()
    hour = State()
    minute = State()
    chanel = State()


logger.info("Состояния загружены!")