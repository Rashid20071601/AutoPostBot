from dataclasses import dataclass
from environs import Env
from typing import Optional
import logging


@dataclass
class TgBot:
    token: str

@dataclass
class LogSettings:
    level: str
    format: str

    def get_level(self) -> int:
        if not isinstance(self.level, str):
            return logging.INFO
        return getattr(logging, self.level.upper(), logging.INFO)

@dataclass
class Config:
    bot: TgBot
    log: LogSettings


def load_config(path: Optional[str] = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        bot=TgBot(token=env.str("BOT_TOKEN", default="")),
        log=LogSettings(level=env("LOG_LEVEL"), format=env("LOG_FORMAT"))
    )