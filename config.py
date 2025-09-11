# Import libraries
from aiogram.fsm.state import State, StatesGroup
import logging

logger = logging.getLogger(__name__)


logger.info("Загрузка конфига...")

class PostState(StatesGroup):
    text = State()
    period = State()
    chanel = State()

logger.info("Конфиг загружен!")