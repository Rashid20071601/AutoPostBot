# ========================= Импорт библиотек ========================= #
import logging
from datetime import date
from typing import List, Optional
from sqlalchemy import select, delete

from database.base import AsyncSessionLocal
from database.models import ChannelORM, MailingORM


# ========================= Настройка логгера ========================= #
logger = logging.getLogger(__name__)


# ========================= Добавление рассылки ========================= #
async def add_mailing(
    text: str,
    image_file_id: Optional[str],
    scheduled_date: date,
    hour: int,
    minute: int,
    channel_id: int,
) -> None:
    """
    Добавляет новую рассылку в базу данных.
    """
    async with AsyncSessionLocal() as session:
        try:
            mailing = MailingORM(
                text=text,
                image_file_id=image_file_id,
                scheduled_date=scheduled_date,
                hour=hour,
                minute=minute,
                channel_id=channel_id,
            )
            session.add(mailing)
            await session.commit()

            logger.info(
                f"✅ Добавлена рассылка (id={mailing.id}) "
                f"для канала={channel_id} на {scheduled_date} {hour:02}:{minute:02}"
            )

        except Exception as e:
            await session.rollback()
            logger.exception(f"❌ Ошибка при добавлении рассылки для channel={channel_id}: {e}")


# ========================= Получение всех рассылок ========================= #
async def get_mailings() -> List[MailingORM]:
    """
    Возвращает все рассылки из базы данных.
    """
    async with AsyncSessionLocal() as session:
        try:
            result = await session.scalars(select(MailingORM))
            mailings = result.all()
            logger.debug(f"📬 Получено {len(mailings)} рассылок из базы.")
            return mailings
        except Exception as e:
            logger.exception(f"Ошибка при получении рассылок: {e}")
            return []


# ========================= Получение рассылки по ID ========================= #
async def get_mailing(mailing_id: int) -> Optional[MailingORM]:
    """
    Возвращает рассылку по её ID.
    """
    async with AsyncSessionLocal() as session:
        try:
            mailing = await session.get(MailingORM, mailing_id)
            if not mailing:
                logger.warning(f"⚠️ Рассылка id={mailing_id} не найдена.")
            return mailing
        except Exception as e:
            logger.exception(f"Ошибка при получении рассылки id={mailing_id}: {e}")
            return None


# ========================= Обновление рассылки ========================= #
async def update_mailing(mailing_id: int, **kwargs) -> Optional[MailingORM]:
    """
    Обновляет указанные поля рассылки.
    Пример: await update_mailing(1, text="Новый текст", enabled=False)
    """
    async with AsyncSessionLocal() as session:
        try:
            mailing = await session.get(MailingORM, mailing_id)
            if not mailing:
                logger.warning(f"⚠️ Не удалось обновить — рассылка {mailing_id} не найдена.")
                return None

            for field, value in kwargs.items():
                if hasattr(mailing, field):
                    setattr(mailing, field, value)
                else:
                    logger.warning(f"Поле '{field}' не существует в модели MailingORM")

            await session.commit()
            logger.info(f"✏️ Рассылка {mailing_id} обновлена: {kwargs}")
            return mailing

        except Exception as e:
            await session.rollback()
            logger.exception(f"❌ Ошибка при обновлении рассылки {mailing_id}: {e}")
            return None


# ========================= Удаление рассылки ========================= #
async def delete_mailing(mailing_id: int) -> bool:
    """
    Удаляет рассылку по ID. Возвращает True, если удаление успешно.
    """
    async with AsyncSessionLocal() as session:
        try:
            deleted = await session.execute(
                delete(MailingORM).where(MailingORM.id == mailing_id)
            )
            await session.commit()

            if deleted.rowcount == 0:
                logger.warning(f"⚠️ Не удалось удалить — рассылка {mailing_id} не найдена.")
                return False

            logger.info(f"🗑 Рассылка {mailing_id} удалена.")
            return True

        except Exception as e:
            await session.rollback()
            logger.exception(f"❌ Ошибка при удалении рассылки {mailing_id}: {e}")
            return False


# ========================= Получение рассылок пользователя ========================= #
async def get_mailings_for_user(user_id: int) -> List[MailingORM]:
    """
    Возвращает все рассылки, привязанные к каналам, которыми владеет пользователь user_id.
    Привязка идёт по полю ChannelORM.channel_id == MailingORM.channel_id.
    """
    async with AsyncSessionLocal() as session:
        try:
            # Подзапрос: все channel_id, принадлежащие user_id
            subq = select(ChannelORM.channel_id).where(ChannelORM.owner_id == user_id)
            result = await session.scalars(select(MailingORM).where(MailingORM.channel_id.in_(subq)))
            mailings = result.all()
            logger.debug(f"📬 Получено {len(mailings)} рассылок для user_id={user_id}.")
            return mailings
        except Exception as e:
            logger.exception(f"Ошибка при получении рассылок для user_id={user_id}: {e}")
            return []
