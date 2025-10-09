from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from database.connection import get_db_url
from config.config import load_config


config = load_config()


engine = create_async_engine(
    url=get_db_url(config),
    echo=config.log.level == "DEBUG",
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)