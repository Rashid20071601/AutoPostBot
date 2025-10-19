from sqlalchemy import BigInteger, ForeignKey, Float, Index, Date
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from typing import Annotated
from datetime import date


intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]

class Base(DeclarativeBase):
    pass


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str] = mapped_column(nullable=True)
    last_name: Mapped[str] = mapped_column(nullable=True)
    channels = relationship("ChannelORM",
                            back_populates="owner",
                            cascade="all, delete-orphan")


class ChannelORM(Base):
    __tablename__ = "channels"

    id: Mapped[intpk]
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    channel_name: Mapped[str] = mapped_column(nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner: Mapped[UserORM] = relationship("UserORM", back_populates="channels")


class MailingORM(Base):
    __tablename__ = "mailings"

    id: Mapped[intpk]
    text: Mapped[str] = mapped_column(nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    hour: Mapped[int] = mapped_column(nullable=False)
    minute: Mapped[int] = mapped_column(nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    enabled: Mapped[bool] = mapped_column(server_default="true", nullable=False)

    __table_args__ = (
        Index("ix_mailing_schedule_enabled", "scheduled_date", "hour", "minute", "enabled", "channel_id", unique=False),
    )