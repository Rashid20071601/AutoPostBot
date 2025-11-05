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
async def send_scheduled_mailings(mailing_id: int, text: str, channel_id: int, bot: Bot) -> None:
    """
    Отправляет запланированную рассылку в указанный канал.
    После успешной отправки — отключает рассылку (enabled=False).
    """
    try:
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
        loop = asyncio.get_running_loop()
        now = datetime.now(ZoneInfo("Europe/Moscow"))

        if not mailings:
            logger.debug("Нет рассылок для синхронизации.")
            return

        for m in mailings:
            mailing_id = m.id
            text = m.text
            scheduled_date = m.scheduled_date
            hour = m.hour
            minute = m.minute
            channel_id = m.channel_id
            enabled = m.enabled

            run_date = datetime.combine(scheduled_date, time(hour=hour, minute=minute, tzinfo=ZoneInfo("Europe/Moscow")))

            # Только будущие включенные рассылки
            if enabled and run_date > now:
                # Проверяем, есть ли уже такая задача
                if scheduler.get_job(str(mailing_id)):
                    logger.debug(f"Задача {mailing_id} уже существует — пропускаем.")
                    continue

                logger.info(
                    f"📅 Планируем рассылку id={mailing_id} "
                    f"на {run_date.strftime('%Y-%m-%d %H:%M:%S')} "
                    f"(сейчас {now.strftime('%Y-%m-%d %H:%M:%S')})"
                )

                # Добавляем задачу с безопасной оберткой
                scheduler.add_job(
                    lambda id=mailing_id, t=text, ch=channel_id, b=bot: asyncio.run_coroutine_threadsafe(
                        send_scheduled_mailings(id, t, ch, b), loop
                    ),
                    trigger="date",
                    run_date=run_date,
                    id=str(mailing_id),
                    replace_existing=True,
                    misfire_grace_time=60,  # если задача пропущена на <= 1 мин, всё ещё отправим
                )

    except Exception as e:
        logger.exception(f"Ошибка при планировании рассылок: {e}")


# ========================= Запуск планировщика ========================= #
async def start_scheduler(bot: Bot) -> None:
    """
    Запускает планировщик и добавляет задачу синхронизации рассылок каждые 60 секунд.
    """
    try:
        # Добавляем задачу, если ещё не существует
        if not scheduler.get_job("sync_mailings"):
            scheduler.add_job(
                sync_mailings,
                trigger="interval",
                minutes=1,
                args=[bot],
                id="sync_mailings",
                replace_existing=True,
            )
            logger.debug("Добавлена повторяющаяся задача sync_mailings (каждую 1 минуту).")

        # Стартуем планировщик, если он ещё не запущен
        if not scheduler.running:
            scheduler.start()
            logger.info("✅ Планировщик успешно запущен и активен!")

    except Exception as e:
        logger.exception(f"❌ Ошибка при запуске планировщика: {e}")
