import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.config import Config, load_config
from handlers import mailing_fsm
from handlers.mailing_datetime import mailing_dialog
from utils.scheduler import start_scheduler
from utils import back



# Функция конфигурирования и запуска бота
async def main() -> None:
    """
    Точка входа в приложение.
    Выполняет настройку логирования, регистрацию роутеров и запуск бота.
    """

    config: Config = load_config()

    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
        filename=config.log.filename,
        filemode=config.log.filemode,
        encoding=config.log.encoding,
        style='{'
    )

    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.workflow_data.update({"bot": bot})

    # 1. ⚙️ Подключение роутеров
    dp.include_router(mailing_fsm.router)
    dp.include_router(back.router)
    dp.include_router(mailing_dialog)

    # 2. 🔗 Регистрация диалога
    setup_dialogs(dp)

    # 3. 🕒 Запуск планировщика
    await start_scheduler(bot)

    # 4. ✔ Старт бота
    logging.info("🚀 Bot is starting...")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        logging.info("🛑 Bot is stopping...")
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())