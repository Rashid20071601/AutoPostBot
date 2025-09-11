# Import libraries
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from dotenv import load_dotenv
import os
import logging

from handlers import callback, start


# --------------- Настройка токена --------------- #
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

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


# =============================  Регистрация callback обработчиков  ============================= #
# Обработчик нажатия кнопки "Вернуться"
dp.callback_query.register(callback.back_to_menu, F.data=="back_to_menu")

# Обработчик нажатия кнопки "Создать рассылку"
dp.callback_query.register(callback.create_post, F.data=="create_post")




# Run polling
if __name__ == '__main__':
    dp.run_polling(bot)