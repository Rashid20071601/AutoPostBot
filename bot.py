# Import libraries
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from environs import Env
import logging

from handlers import posting, start, back
from config import PostState


# --------------- Настройка токена --------------- #
env = Env()
env.read_env()

BOT_TOKEN = env("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("Переменная окружения BOT_TOKEN не найдена. Проверь .env файл.")


# --------------- Инициализация бота и диспетчера --------------- #
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# --------------- Настройка логирования --------------- #
formatter = logging.Formatter(
    '[{asctime}] #{levelname:8} {filename}:{lineno} - {name} - {message}',
    style='{'
)

file_handler = logging.FileHandler('logs.log', encoding="utf-8", mode='w')
file_handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[file_handler])
logger = logging.getLogger(__name__)
logger.info("Бот запущен!...")



# =============================  Регистрация обработчиков команд  ============================= #
# Обработчик команды /start
dp.message.register(start.send_welcome, Command(commands="start"))

# Обработчик команды /help
dp.message.register(start.send_help, Command(commands="help"))


# =============================  Регистрация хендлеров  ============================= #
# Обработчик нажатия кнопки "Вернуться"
dp.callback_query.register(back.back_to_menu, F.data=="back_to_menu")

# Обработчик нажатия кнопки "Создать рассылку"
dp.callback_query.register(posting.handle_create_mailing, F.data=="create_post")

# Обработчик хендлера для ввода текста рассылки
dp.message.register(posting.handle_mailing_text, PostState.text)

# Обработчик хендлера для ввода интервала публикации
dp.message.register(posting.handle_mailing_interval, PostState.interval)




# Run polling
if __name__ == '__main__':
    dp.run_polling(bot)