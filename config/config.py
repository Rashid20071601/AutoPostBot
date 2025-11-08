# ========================= Импорт библиотек ========================= #
from dataclasses import dataclass
from typing import Optional
from environs import Env
import logging


# ========================= Настройки Telegram Bot ========================= #
@dataclass(slots=True)
class TgBotSettings:
    token: str


# ========================= Настройки логирования ========================= #
@dataclass(slots=True)
class LogSettings:
    level: str
    format: str
    filename: str
    filemode: str
    encoding: str

    def as_dict(self) -> dict:
        """Возвращает словарь для передачи в logging.basicConfig."""
        return {
            "level": self.get_level(),
            "format": self.format,
            "filename": self.filename,
            "filemode": self.filemode,
            "encoding": self.encoding,
            "style": "{",
        }

    def get_level(self) -> int:
        """Возвращает числовой уровень логирования."""
        try:
            return getattr(logging, self.level.upper())
        except AttributeError:
            logging.warning(f"⚠️ Некорректный уровень логирования '{self.level}', используем INFO.")
            return logging.INFO


# ========================= Настройки базы данных ========================= #
@dataclass(slots=True)
class DBSettings:
    host: str
    port: int
    user: str
    password: str
    name: str

    def build_dsn(self, driver: str = "asyncpg") -> str:
        """
        Возвращает строку подключения в формате:
        postgresql+asyncpg://user:pass@host:port/dbname
        """
        return f"postgresql+{driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


# ========================= Главный конфиг ========================= #
@dataclass(slots=True)
class Config:
    bot: TgBotSettings
    log: LogSettings
    db: DBSettings
    environment: str = "development"


# ========================= Загрузка конфигурации ========================= #
def load_config(path: Optional[str] = None) -> Config:
    """
    Загружает конфигурацию из .env файла.
    Возвращает объект Config с секциями bot, log и db.
    """
    env = Env()
    env.read_env(path)

    bot_token = env.str("BOT_TOKEN", "")
    if not bot_token:
        raise ValueError("❌ BOT_TOKEN отсутствует в .env — бот не может быть запущен!")

    config = Config(
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
        environment=env.str("ENV", "development"),
    )

    logging.getLogger(__name__).info(f"🌍 Конфигурация успешно загружена ({config.environment})")
    return config
