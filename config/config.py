# ========================= Импорт библиотек ========================= #
from dataclasses import dataclass
from environs import Env
from typing import Optional
import logging


# ========================= Настройки Telegram Bot ========================= #
@dataclass
class TgBotSettings:
    token: str


# ========================= Настройки логирования ========================= #
@dataclass
class LogSettings:
    level: str
    format: str
    filename: str
    filemode: str
    encoding: str

    def get_level(self) -> int:
        """Возвращает уровень логирования как int для logging.basicConfig"""
        if not isinstance(self.level, str):
            return logging.INFO
        return getattr(logging, self.level.upper(), logging.INFO)


# ========================= Настройки БД ========================= #
@dataclass
class DBSettings:
    host: str
    port: int
    user: str
    password: str
    name: str


# ========================= Главный конфиг ========================= #
@dataclass
class Config:
    bot: TgBotSettings
    log: LogSettings
    db: DBSettings


# ========================= Загрузка конфигурации ========================= #
def load_config(path: Optional[str] = None) -> Config:
    """
    Загружает конфигурацию из .env файла.
    Возвращает объект Config с секциями bot, log и db.
    """
    env = Env()
    env.read_env(path)

    # Безопасное чтение с дефолтами
    bot_token = env.str("BOT_TOKEN", default="")
    if not bot_token:
        raise ValueError("❌ Не найден BOT_TOKEN в .env файле — бот не может быть запущен!")

    return Config(
        bot=TgBotSettings(token=bot_token),
        log=LogSettings(
            level=env.str("LOG_LEVEL", "INFO"),
            format=env.str("LOG_FORMAT", "[{asctime}] #{levelname:<8} {filename}:{lineno} - {message}"),
            filename=env.str("LOG_FILENAME", "bot.log"),
            filemode=env.str("LOG_FILEMODE", "a"),
            encoding=env.str("LOG_ENCODING", "utf-8"),
        ),
        db=DBSettings(
            host=env.str("POSTGRES_HOST", "localhost"),
            port=env.int("POSTGRES_PORT", 5432),
            user=env.str("POSTGRES_USER", "postgres"),
            password=env.str("POSTGRES_PASSWORD", ""),
            name=env.str("POSTGRES_DB", "autopostbot"),
        ),
    )
