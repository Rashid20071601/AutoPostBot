from sqlalchemy import BigInteger, ForeignKey, REAL
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import DeclarativeBase
from typing import Annotated


intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

class Base(DeclarativeBase):
    pass


class UsersORM(Base):
    __tablename__ = "users"

    id: Mapped[intpk]
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)

class ChannelsORM(Base):
    __tablename__ = "channels"

    id: Mapped[intpk]
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

class MailingsORM(Base):
    __tablename__ = "mailings"

    id: Mapped[intpk]
    text: Mapped[str]
    hour: Mapped[int]
    minute: Mapped[int]
    channel_id: Mapped[int]
    enabled: Mapped[bool] = mapped_column(server_default="True")
    last_sent: Mapped[float] = mapped_column(REAL, server_default="0")
