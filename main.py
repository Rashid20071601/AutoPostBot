# ========================= Импорт библиотек ========================= #
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram_dialog import setup_dialogs
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.config import Config, load_config
from handlers import mailing_fsm, mailing_manage, mailing_pagination
from handlers.mailing_datetime import mailing_dialog
from utils.scheduler import start_scheduler
from utils import back
from database.base import test_db_connection


# ========================= Основная точка входа ========================= #
async def main() -> None:
    """
    Точка входа в приложение.
    Настраивает логирование, инициализирует бота, диспетчер, планировщик и запускает polling.
    """
    # ---------- 1. Загрузка конфигурации ----------
    config: Config = load_config()

    # ---------- 2. Настройка логирования ----------
    logging.basicConfig(**config.log.as_dict())
    logger = logging.getLogger(__name__)
    logger.info("🧩 Конфигурация и логирование инициализированы")

    # ---------- 3. Инициализация бота и диспетчера ----------
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.workflow_data.update({"bot": bot})
    logger.info("🤖 Бот успешно инициализирован")

    # ---------- 4. Подключение роутеров и диалогов ----------
    for router in (mailing_fsm.router, mailing_manage.router, back.router, mailing_dialog, mailing_pagination.router):
        dp.include_router(router)
    setup_dialogs(dp)
    logger.info("🧭 Диалоги и роутеры подключены")

    # ---------- 5. Запуск планировщика ----------
    await start_scheduler(bot)
    logger.info("⏰ Планировщик успешно запущен")

    # ---------- 6. Тест подключения к базе данных ----------
    await test_db_connection()

    # ---------- 7. Запуск бота ----------
    logger.info("🚀 Бот запускается... (режим polling)")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except (KeyboardInterrupt, SystemExit):
        logger.warning("🛑 Остановка бота по сигналу пользователя")
    except Exception as e:
        logger.exception(f"❌ Критическая ошибка в работе бота: {e}")
    finally:
        logger.info("🧹 Завершение работы, закрываем соединения...")
        await bot.session.close()
        logger.info("✅ Бот остановлен корректно.")


# ========================= Запуск через asyncio.run ========================= #
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("🛑 Завершено вручную.")
