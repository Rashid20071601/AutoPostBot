import asyncio
import logging

from aiogram import Bot, Dispatcher
from config.config import Config, load_config
from handlers import user
from database.db import init_db
from handlers.user import load_mailings, scheduler



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
    dp.include_router(user.router)

    # 3. Запуск фонового воркера
    asyncio.create_task(load_mailings(bot))
    scheduler.start()

    # 4. Старт бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
