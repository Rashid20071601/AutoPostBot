# Import libraries
from aiogram.fsm.state import State, StatesGroup
import logging

logger = logging.getLogger(__name__)


logger.debug("Загрузка состояний...")


# --------------- Настройка состояний --------------- #
class PostState(StatesGroup):
    text = State()
    interval = State()
    chanel = State()


logger.info("Состояния загружены!")