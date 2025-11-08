# ========================= Импорт библиотек ========================= #
import logging
from typing import List, Optional
from sqlalchemy import select

from database.base import AsyncSessionLocal
from database.models import UserORM


# ========================= Настройка логгера ========================= #
logger = logging.getLogger(__name__)


# ========================= Добавление пользователя ========================= #
async def create_user(user_id: int, first_name: Optional[str], last_name: Optional[str]) -> None:
    """
    Добавляет нового пользователя в базу.
    Если пользователь уже существует — пропускает.
    """
    logger.debug(f"Создание пользователя id={user_id} ({first_name} {last_name})")

    async with AsyncSessionLocal() as session:
        try:
            if await session.get(UserORM, user_id):
                logger.info(f"Пользователь {user_id} уже существует — пропуск.")
                return

            session.add(UserORM(id=user_id, first_name=first_name, last_name=last_name))
            await session.commit()
            logger.info(f"✅ Новый пользователь добавлен: id={user_id}")

        except Exception as e:
            await session.rollback()
            logger.exception(f"❌ Ошибка при создании пользователя {user_id}: {e}")


# ========================= Получение всех пользователей ========================= #
async def get_users() -> List[UserORM]:
    """
    Возвращает список всех пользователей.
    """
    logger.debug("📡 Запрос всех пользователей")
    async with AsyncSessionLocal() as session:
        try:
            result = await session.scalars(select(UserORM))
            users = result.all()
            logger.debug(f"Получено {len(users)} пользователей")
            return users
        except Exception as e:
            logger.exception(f"Ошибка при получении списка пользователей: {e}")
            return []


# ========================= Проверка существования пользователя ========================= #
async def user_exists(user_id: int) -> bool:
    """
    Проверяет, существует ли пользователь в базе.
    Возвращает True, если найден.
    """
    async with AsyncSessionLocal() as session:
        try:
            exists = await session.scalar(select(UserORM.id).where(UserORM.id == user_id))
            logger.debug(f"Проверка существования пользователя {user_id}: {'✅' if exists else '❌'}")
            return exists is not None
        except Exception as e:
            logger.exception(f"Ошибка при проверке пользователя {user_id}: {e}")
            return False
