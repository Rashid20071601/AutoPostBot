# ========================= Импорт библиотек ========================= #
from dataclasses import dataclass
from environs import Env
from typing import Optional
import logging
import os


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
    Автоматически выбирает .env.local или .env.production в зависимости от ENV.
    """
    env = Env()

    # 1️⃣ Определяем окружение (по умолчанию — local)
    env_type = os.getenv("ENV", "production").lower()
    env_file = path or f".env.{env_type}"

    # 2️⃣ Проверяем наличие файла окружения
    if not os.path.exists(env_file):
        raise FileNotFoundError(f"❌ Не найден файл окружения: {env_file}")

    # 3️⃣ Загружаем переменные окружения
    env.read_env(env_file)

    # 4️⃣ Проверяем обязательные параметры
    bot_token = env.str("BOT_TOKEN", default="")
    if not bot_token:
        raise ValueError("❌ Не найден BOT_TOKEN в .env файле — бот не может быть запущен!")

    # 5️⃣ Создаём объект конфигурации
    config = Config(
        bot=TgBotSettings(token=bot_token),
        log=LogSettings(
            level=env.str("LOG_LEVEL", "INFO"),
            format=env.str("LOG_FORMAT", "[{asctime}] #{levelname:<8} {filename}:{lineno} - {message}"),
            filename=env.str("LOG_FILENAME", "logs.log"),
            filemode=env.str("LOG_FILEMODE", "w"),
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

    return config