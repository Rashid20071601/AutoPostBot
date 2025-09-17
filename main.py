import asyncio
import logging

from aiogram import Bot, Dispatcher
from config.config import Config, load_config
from handlers import user



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

    dp.include_router(user.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())
