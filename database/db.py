from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import insert, delete, update, select
from typing import List, Tuple, Optional

from database.connection import db_url_asyncpg
from database.models import Base, UsersORM, ChannelsORM, MailingsORM



async_engine = create_async_engine(
    url=db_url_asyncpg(),
    echo=True,
    pool_size=5,
    max_overflow=10
)

async def create_table():
    async_engine.echo=False
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_engine.echo=True


async def add_mailing(text, hour, minute, channel_id):
    async with async_engine.begin() as conn:
        await conn.execute(
            insert(MailingsORM).values(
                text=text,
                hour=hour,
                minute=minute,
                channel_id=channel_id,
            )
        )
        await conn.commit()

async def get_mailings() -> List[Tuple]:
    async with async_engine.begin() as conn:
        async with conn.execute(select(MailingsORM)) as res:
            return res.fetchall()

async def get_mailing(mailing_id: int) -> Optional[Tuple]:
    async with async_engine.begin() as conn:
        async with conn.execute(select(MailingsORM).where(MailingsORM.id==mailing_id)) as res:
            return res.fetchone()

async def update_mailing(
        mailing_id: int,
        text: Optional[str] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        enabled: Optional[int] = None
    ) -> None:
    async with async_engine.begin() as conn:
        values = {k:v for k,v in {
            "text":text,
            "hour":hour,
            "minute":minute,
            "enabled":enabled,
        }.items() if v is not None}

        if values:
            await conn.execute(update(MailingsORM).where(MailingsORM.id==mailing_id).values(**values))
        await conn.commit()

async def delete_mailing(mailing_id: int) -> None:
    async with async_engine.begin() as conn:
        await conn.execute(delete(MailingsORM).where(MailingsORM.id==mailing_id))
        await conn.commit()

async def update_last_sent(mailing_id: int, timestamp: int) -> None:
    async with async_engine.begin() as conn:
        await conn.execute(update(MailingsORM).where(MailingsORM.id==mailing_id).values(last_sent=timestamp))
        await conn.commit()