def get_db_url(conf) -> str:
    return f"postgresql+asyncpg://{conf.db.user}:{conf.db.password}@{conf.db.host}:{conf.db.port}/{conf.db.name}"
