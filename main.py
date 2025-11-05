# ========================= Импорт библиотек ========================= #
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.config import Config, load_config
from handlers import mailing_fsm, mailing_manage
from handlers.mailing_datetime import mailing_dialog
from utils.scheduler import start_scheduler
from utils import back


# ========================= Основная точка входа ========================= #
async def main() -> None:
    """
    Точка входа в приложение.
    Настраивает логирование, создаёт бота и диспетчер, подключает роутеры и запускает polling.
    """

    # ========================= 1. Загрузка конфигурации ========================= #
    config: Config = load_config()

    # ========================= 2. Настройка логирования ========================= #
    logging.basicConfig(
        level=logging.getLevelName(level=config.log.level),
        format=config.log.format,
        filename=config.log.filename,
        filemode=config.log.filemode,
        encoding=config.log.encoding,
        style='{'
    )

    logger = logging.getLogger(__name__)
    logger.info("🧩 Конфигурация и логирование инициализированы")

    # ========================= 3. Инициализация бота ========================= #
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # глобально задаём HTML-разметку
    )
    dp = Dispatcher()

    # можно хранить общие зависимости в workflow_data
    dp.workflow_data.update({"bot": bot})
    logger.info("🤖 Бот успешно инициализирован")

    # ========================= 4. Подключение роутеров ========================= #
    dp.include_router(mailing_fsm.router)
    dp.include_router(mailing_manage.router)
    dp.include_router(back.router)
    dp.include_router(mailing_dialog)

    # ========================= 5. Регистрация диалогов ========================= #
    setup_dialogs(dp)
    logger.info("🧭 Диалоги и роутеры подключены")

    # ========================= 6. Запуск планировщика ========================= #
    await start_scheduler(bot)
    logger.info("⏰ Планировщик успешно запущен")

    # ========================= 7. Запуск polling ========================= #
    logger.info("🚀 Бот запускается...")

    try:
        # Удаляем webhook, чтобы бот перешёл в polling-режим
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logger.warning("🛑 Остановка бота по сигналу пользователя")
    except Exception as e:
        logger.exception(f"❌ Критическая ошибка в работе бота: {e}")
    finally:
        logger.info("🧹 Завершение работы, закрываем соединения...")
        await bot.close()
        logger.info("✅ Бот остановлен корректно.")


# ========================= Запуск через asyncio.run ========================= #
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Завершено вручную.")