from config.config import Config, load_config

def db_url_asyncpg():
    config: Config = load_config()
    return f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.name}"
