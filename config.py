# Import libraries
from aiogram.fsm.state import State, StatesGroup
import logging
from environs import Env

logger = logging.getLogger(__name__)


logger.debug("Загрузка конфига...")



# --------------- Настройка состояний --------------- #
class PostState(StatesGroup):
    text = State()
    interval = State()
    chanel = State()

# --------------- Настройка токена --------------- #
env = Env()
env.read_env()

BOT_TOKEN = env("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("Переменная окружения BOT_TOKEN не найдена. Проверь .env файл.")



logger.info("Конфиг загружен!")