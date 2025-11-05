# ========================= Импорт библиотек ========================= #
from sqlalchemy import select
from typing import List, Optional
import logging

from database.base import AsyncSessionLocal
from database.models import UserORM


# ========================= Настройка логгера ========================= #
logger = logging.getLogger(__name__)


# ========================= CRUD-функции ========================= #
async def create_user(user_id: int, first_name: Optional[str], last_name: Optional[str]) -> None:
    """
    Добавляет нового пользователя в базу.
    Если пользователь уже существует — пропускает.
    """
    try:
        async with AsyncSessionLocal() as session:
            # Проверяем, есть ли пользователь
            existing_user = await session.get(UserORM, user_id)
            if existing_user:
                logger.debug(f"Пользователь {user_id} уже существует, пропуск добавления.")
                return

            user = UserORM(
                id=user_id,
                first_name=first_name,
                last_name=last_name,
            )
            session.add(user)
            await session.commit()

            logger.info(f"✅ Новый пользователь добавлен: id={user_id}")

    except Exception as e:
        logger.exception(f"❌ Ошибка при создании пользователя {user_id}: {e}")


async def get_users() -> List[UserORM]:
    """
    Возвращает список всех пользователей.
    """
    logger.debug("Запрос списка всех пользователей.")
    try:
        async with AsyncSessionLocal() as session:
            result = await session.scalars(select(UserORM))
            users = result.all()
            logger.debug(f"Получено {len(users)} пользователей из базы.")
            return users
    except Exception as e:
        logger.exception(f"Ошибка при получении списка пользователей: {e}")
        return []


async def user_exists(user_id: int) -> bool:
    """
    Проверяет, существует ли пользователь в базе.
    Возвращает True, если найден.
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.scalar(select(UserORM.id).where(UserORM.id == user_id))
            exists = result is not None
            logger.debug(f"Проверка существования пользователя {user_id}: {exists}")
            return exists
    except Exception as e:
        logger.exception(f"Ошибка при проверке пользователя {user_id}: {e}")
        return False
