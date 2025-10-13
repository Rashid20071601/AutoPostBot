from datetime import date
from sqlalchemy import select, update, delete
from typing import List, Optional
import logging

from database.base import AsyncSessionLocal
from database.models import UserORM

logger = logging.getLogger(__name__)


async def create_user(
        user_id: int,
        first_name: str,
        last_name: str
        ) -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            u = UserORM(
                id=user_id,
                first_name=first_name,
                last_name=last_name
            )
            session.add(u)
            await session.commit()


async def get_users() -> List[UserORM]:
    """Вернуть всех пользователей."""
    logger.debug("Получение всех пользователей")
    async with AsyncSessionLocal() as session:
        res = await session.scalars(select(UserORM))
        users = res.all()
        return users

async def user_exists(user_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        res = await session.scalars(select(UserORM, user_id))
        return res is not None