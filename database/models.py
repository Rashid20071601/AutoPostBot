# ========================= Импорт библиотек ========================= #
from datetime import date
from typing import Annotated, List, Optional

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Date,
    Index,
    Boolean,
    String,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    relationship,
)

# ========================= Общие типы ========================= #
intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]


# ========================= Базовый класс ========================= #
class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""
    pass


# ========================= Модель пользователей ========================= #
class UserORM(Base):
    """
    Пользователь Telegram, взаимодействующий с ботом.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)  # Telegram ID
    first_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    channels: Mapped[List["ChannelORM"]] = relationship(
        "ChannelORM",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return f"<UserORM id={self.id} name='{full_name}'>"


# ========================= Модель каналов ========================= #
class ChannelORM(Base):
    """
    Telegram-каналы, к которым привязан пользователь.
    """
    __tablename__ = "channels"

    id: Mapped[intpk]
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    channel_name: Mapped[str] = mapped_column(String(128), nullable=False)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    owner: Mapped["UserORM"] = relationship("UserORM", back_populates="channels")

    def __repr__(self) -> str:
        return f"<ChannelORM id={self.channel_id} name='{self.channel_name}'>"


# ========================= Модель рассылок ========================= #
class MailingORM(Base):
    """
    Таблица с запланированными рассылками.
    """
    __tablename__ = "mailings"

    id: Mapped[intpk]
    text: Mapped[str] = mapped_column(String, nullable=False)
    image_file_id: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    hour: Mapped[int] = mapped_column(nullable=False)
    minute: Mapped[int] = mapped_column(nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    __table_args__ = (
        Index(
            "ix_mailing_schedule_enabled",
            "scheduled_date",
            "hour",
            "minute",
            "enabled",
            "channel_id",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<MailingORM id={self.id} "
            f"date={self.scheduled_date} time={self.hour:02}:{self.minute:02} "
            f"channel={self.channel_id} enabled={self.enabled}>"
        )
