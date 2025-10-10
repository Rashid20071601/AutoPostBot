import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo
import logging
from aiogram import Bot
from datetime import datetime, time

from database.crud.mailings import get_mailings, update_mailing


scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))
logger = logging.getLogger(__name__)



async def send_scheduled_mailings(mailing_id: int, text: str, channel_id: int, bot:Bot) -> None:
    """Проверяет запланированные рассылки и отправляет их"""
    try:
        await bot.send_message(channel_id, text)
        await update_mailing(mailing_id=mailing_id, enabled=False)
        logger.info(f"✅ Рассылка {mailing_id} отправлена в канал {channel_id} с текстом: {text[:50]}...")
    except Exception as e:
        logger.exception(f"Ошибка при отправки рассылки: {e}")


async def start_scheduler(bot: Bot) -> None:
    try:
        mailings = await get_mailings()
        for m in mailings:
            mailing_id = m.id
            text = m.text
            scheduled_date = m.scheduled_date
            hour = m.hour
            minute = m.minute
            channel_id = m.channel_id
            enabled = m.enabled
            if enabled:
                run_date = datetime.combine(scheduled_date, time(hour=hour, minute=minute))
                scheduler.add_job(
                    lambda id=mailing_id, t=text, ch=channel_id, b=bot: asyncio.create_task(send_scheduled_mailings(id, t, ch, b)),
                    trigger="date",
                    run_date=run_date,
                    id=str(mailing_id),
                    replace_existing=True
                )
        if not scheduler.running:
            scheduler.start()
            logger.info("Планировщик задача успешно запущен!")
    except Exception as e:
        logger.exception(f"Ошибка при установке планировщика: {e}")