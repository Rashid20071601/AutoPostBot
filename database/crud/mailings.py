# ========================= Импорт библиотек ========================= #
from datetime import date
from sqlalchemy import select
from typing import List, Optional
import logging

from database.base import AsyncSessionLocal
from database.models import MailingORM


# ========================= Настройка логгера ========================= #
logger = logging.getLogger(__name__)


# ========================= Добавление рассылки ========================= #
async def add_mailing(
    text: str,
    scheduled_date: date,
    hour: int,
    minute: int,
    channel_id: int
) -> None:
    """
    Добавляет новую рассылку в базу данных.
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                mailing = MailingORM(
                    text=text,
                    scheduled_date=scheduled_date,
                    hour=hour,
                    minute=minute,
                    channel_id=channel_id,
                )
                session.add(mailing)
                await session.commit()

                logger.info(
                    f"✅ Добавлена рассылка (id={mailing.id}) для канала={channel_id} "
                    f"на {scheduled_date} {hour:02}:{minute:02}"
                )

    except Exception as e:
        logger.exception(f"❌ Ошибка при добавлении рассылки для channel={channel_id}: {e}")


# ========================= Получение всех рассылок ========================= #
async def get_mailings() -> List[MailingORM]:
    """
    Возвращает все рассылки из базы данных.
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.scalars(select(MailingORM))
            mailings = result.all()
            logger.debug(f"📬 Получено {len(mailings)} рассылок из базы данных.")
            return mailings
    except Exception as e:
        logger.exception(f"Ошибка при получении рассылок: {e}")
        return []


# ========================= Получение рассылки по ID ========================= #
async def get_mailing(mailing_id: int) -> Optional[MailingORM]:
    """
    Возвращает рассылку по её ID.
    """
    try:
        async with AsyncSessionLocal() as session:
            mailing = await session.get(MailingORM, mailing_id)
            if not mailing:
                logger.warning(f"Рассылка {mailing_id} не найдена.")
            return mailing
    except Exception as e:
        logger.exception(f"Ошибка при получении рассылки id={mailing_id}: {e}")
        return None


# ========================= Обновление рассылки ========================= #
async def update_mailing(mailing_id: int, **kwargs) -> Optional[MailingORM]:
    """
    Обновляет поля рассылки.
    Пример: await update_mailing(1, text="Новый текст", enabled=False)
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                mailing = await session.get(MailingORM, mailing_id)

                if not mailing:
                    logger.warning(f"⚠️ Не удалось обновить — рассылка {mailing_id} не найдена.")
                    return None

                for key, value in kwargs.items():
                    setattr(mailing, key, value)

                await session.commit()
                logger.info(f"✏️ Рассылка {mailing_id} обновлена: {kwargs}")
                return mailing

    except Exception as e:
        logger.exception(f"❌ Ошибка при обновлении рассылки {mailing_id}: {e}")
        return None


# ========================= Удаление рассылки ========================= #
async def delete_mailing(mailing_id: int) -> bool:
    """
    Удаляет рассылку из базы данных.
    """
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                mailing = await session.get(MailingORM, mailing_id)

                if not mailing:
                    logger.warning(f"⚠️ Не удалось удалить — рассылка {mailing_id} не найдена.")
                    return False

                await session.delete(mailing)
                await session.commit()

                logger.info(f"🗑 Рассылка {mailing_id} удалена.")
                return True

    except Exception as e:
        logger.exception(f"❌ Ошибка при удалении рассылки {mailing_id}: {e}")
        return False
