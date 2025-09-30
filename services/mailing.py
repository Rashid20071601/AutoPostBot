from aiogram import Bot
import logging
import time

from database.db import update_last_sent, get_mailings
from utils import scheduler


logger = logging.getLogger(__name__)



async def send_mailing(mailing_id: int, text: str, channel_id: int, bot: Bot) -> None:
    try:
        await bot.send_message(channel_id, text)
        await update_last_sent(mailing_id, time.time())
    except Exception as e:
        logger.exception(f"Ошибка отправки рассылки {mailing_id} в канал {channel_id}: {e}")


async def load_mailings(bot: Bot) -> None:
    try:
        mailings = await get_mailings()
        for m in mailings:
            mailing_id, text, hour, minute, channel_id, enabled, last_sent = m
            if enabled:
                scheduler.add_job(
                    send_mailing,
                    trigger="cron",
                    hour=hour,
                    minute=minute,
                    args=[mailing_id, text, channel_id, bot],
                    id=str(mailing_id),
                    replace_existing=True
                )
    except Exception as e:
        logger.exception(f"Ошибка добавления рассылка {mailing_id} в планировщик: {e}")