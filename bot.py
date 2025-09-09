# Импорт библиотек
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import os
from dotenv import load_dotenv

from handlers import start


# --------------- Настройка токена --------------- #
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Токен бота не найден! Проверь .env файл.")


# --------------- Инициализация бота и диспетчера --------------- #
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()



# =============================  Регистрация обработчиков команд  ============================= #
# Обработчик команды /start
dp.message.register(start.send_welcome, Command(commands="start"))




# Run polling
if __name__ == '__main__':
    dp.run_polling(bot)