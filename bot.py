# Импорт библиотек
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from dotenv import load_dotenv
import os

from handlers import start, back


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

# Обработчик команды /help
dp.message.register(start.send_help, Command(commands="help"))

# Обработчик нажатия кнопки "Назад"
dp.callback_query.register(back.back_to_menu, F.data=="back_to_menu")




# Run polling
if __name__ == '__main__':
    dp.run_polling(bot)