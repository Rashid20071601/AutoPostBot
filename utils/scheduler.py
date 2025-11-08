# ========================= Импорт библиотек ========================= #
import asyncio
import logging
from datetime import datetime, time
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

from database.crud.mailings import get_mailings, update_mailing


# ========================= Инициализация ========================= #
scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))
logger = logging.getLogger(__name__)


# ========================= Отправка рассылки ========================= #
async def send_scheduled_mailings(
    mailing_id: int,
    text: str,
    image_file_id: str | None,
    channel_id: int,
    bot: Bot
) -> None:
    """
    Отправляет запланированную рассылку в указанный канал.
    После успешной отправки — отключает рассылку (enabled=False).
    """
    try:
        if image_file_id:
            await bot.send_photo(channel_id, photo=image_file_id, caption=text)
        else:
            await bot.send_message(channel_id, text)

        await update_mailing(mailing_id=mailing_id, enabled=False)

        logger.info(
            f"✅ Рассылка {mailing_id} отправлена в канал {channel_id}. "
            f"Текст (первые 50 символов): {text[:50]}..."
        )

    except Exception as e:
        logger.exception(f"❌ Ошибка при отправке рассылки (id={mailing_id}, ch={channel_id}): {e}")


# ========================= Синхронизация рассылок ========================= #
async def sync_mailings(bot: Bot) -> None:
    """
    Проверяет актуальные рассылки в БД и добавляет их в APScheduler,
    если они ещё не были запланированы.
    """
    try:
        mailings = await get_mailings()
        if not mailings:
            logger.debug("Нет рассылок для синхронизации.")
            return

        now = datetime.now(ZoneInfo("Europe/Moscow"))
        loop = asyncio.get_running_loop()

        for mailing in mailings:
            run_date = datetime.combine(
                mailing.scheduled_date,
                time(hour=mailing.hour, minute=mailing.minute, tzinfo=ZoneInfo("Europe/Moscow"))
            )

            if not mailing.enabled or run_date <= now:
                continue  # Пропускаем неактивные или просроченные рассылки

            if scheduler.get_job(str(mailing.id)):
                logger.debug(f"Задача {mailing.id} уже существует — пропускаем.")
                continue

            logger.info(
                f"📅 Планируем рассылку id={mailing.id} "
                f"на {run_date.strftime('%Y-%m-%d %H:%M:%S')} "
                f"(сейчас {now.strftime('%Y-%m-%d %H:%M:%S')})"
            )

            # Безопасно планируем отправку
            scheduler.add_job(
                lambda m=mailing: asyncio.run_coroutine_threadsafe(
                    send_scheduled_mailings(
                        m.id, m.text, m.image_file_id, m.channel_id, bot
                    ),
                    loop
                ),
                trigger="date",
                run_date=run_date,
                id=str(mailing.id),
                replace_existing=True,
                misfire_grace_time=60,  # если задача просрочена <= 1 мин, всё ещё отправим
            )

    except Exception as e:
        logger.exception(f"Ошибка при синхронизации рассылок: {e}")


# ========================= Запуск планировщика ========================= #
async def start_scheduler(bot: Bot) -> None:
    """
    Запускает планировщик и добавляет задачу синхронизации рассылок каждые 60 секунд.
    """
    try:
        if not scheduler.get_job("sync_mailings"):
            scheduler.add_job(
                sync_mailings,
                trigger="interval",
                minutes=1,
                args=[bot],
                id="sync_mailings",
                replace_existing=True,
            )
            logger.debug("🌀 Задача sync_mailings добавлена (каждую 1 минуту).")

        if not scheduler.running:
            scheduler.start()
            logger.info("✅ Планировщик успешно запущен!")

    except Exception as e:
        logger.exception(f"❌ Ошибка при запуске планировщика: {e}")
