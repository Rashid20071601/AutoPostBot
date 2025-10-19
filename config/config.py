from dataclasses import dataclass
from environs import Env
from typing import Optional
import logging


@dataclass
class TgBotSettings:
    token: str

@dataclass
class LogSettings:
    level: str
    format: str
    filename: str
    filemode: str
    encoding: str

    def get_level(self) -> int:
        if not isinstance(self.level, str):
            return logging.INFO
        return getattr(logging, self.level.upper(), logging.INFO)

@dataclass
class DBSettings:
    host: str
    port: int
    user: str
    password: str
    name: str

@dataclass
class Config:
    bot: TgBotSettings
    log: LogSettings
    db: DBSettings


def load_config(path: Optional[str] = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        bot=TgBotSettings(token=env.str("BOT_TOKEN", default="")),
        log=LogSettings(
            level=env("LOG_LEVEL"),
            format=env("LOG_FORMAT"),
            filename=env("LOG_FILENAME"),
            filemode=env("LOG_FILEMODE"),
            encoding=env("LOG_ENCODING"),
            ),
        db=DBSettings(
            host=env.str("POSTGRES_HOST"),
            port=env.int("POSTGRES_PORT"),
            user=env.str("POSTGRES_USER"),
            password=env.str("POSTGRES_PASSWORD"),
            name=env.str("POSTGRES_DB"),
        ),
    )