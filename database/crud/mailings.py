from sqlalchemy import select, update, delete
from typing import List, Optional

from database.base import AsyncSessionLocal
from database.models import UserORM, ChannelORM, MailingORM


async def add_mailing(
        text: str,
        hour: int,
        minute: int,
        channel_name: int
        ) -> MailingORM:
    async with AsyncSessionLocal() as session:
        m = MailingORM(
            text=text,
            hour=hour,
            minute=minute,
            channel_name=channel_name
        )
        session.add(m)
        await session.commit()
        await session.refresh(m)
        return m


async def get_mailings() -> List[MailingORM]:
    async with AsyncSessionLocal() as session:
        res = await session.scalars(select(MailingORM))
        return res.all()


async def get_mailing(mailing_id: int) -> Optional[MailingORM]:
    async with AsyncSessionLocal() as session:
        return await session.get(MailingORM, mailing_id)


async def update_mailing(
        mailing_id: int,
        **kwargs
        ) -> Optional[MailingORM]:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            mailing = await session.get(MailingORM, mailing_id)

            if not mailing:
                return None

            for k, v in kwargs.items():
                setattr(mailing, k, v)

        await session.commit()
        return mailing


async def delete_mailing(mailing_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            m = await session.get(MailingORM, mailing_id)

            if not m:
                return False

            await session.delete(m)
        return True


async def update_last_sent(mailing_id: int, timestamp: int) -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            m = await session.get(MailingORM, mailing_id)

            if m:
                m.last_sent = timestamp