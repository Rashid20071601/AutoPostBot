import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs

from config.config import Config, load_config
from handlers import mailing_fsm, mailing_manage
from services.mailing_datetime import mailing_dialog
from utils import back
from database.db import init_db



# Функция конфигурирования и запуска бота
async def main() -> None:
    config: Config = load_config()

    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
        style='{'
    )

    bot = Bot(token=config.bot.token)
    dp = Dispatcher()
    dp.workflow_data.update({"bot": bot})

    # 1. Инициализация базы
    await init_db()

    # 2. Подключение роутеров
    dp.include_router(mailing_fsm.router)
    dp.include_router(mailing_manage.router)
    dp.include_router(back.router)
    dp.include_router(mailing_dialog)

    # 3. Регистрация диалога
    setup_dialogs(dp)

    # 4. Запуск фонового воркера
    # asyncio.create_task(load_mailings(bot))
    # scheduler.start()

    # 5. Старт бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
