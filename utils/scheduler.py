from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo
import logging


scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))
logger = logging.getLogger(__name__)


def start_scheduler() -> None:
    if not scheduler.running:
        scheduler.start()
        logger.info("Планировщик задача успешно запущен!")