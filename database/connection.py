def get_db_url(conf) -> str:
    """
    Формирует строку подключения к PostgreSQL с asyncpg-драйвером.
    """
    user = conf.db.user
    password = conf.db.password
    host = conf.db.host
    port = conf.db.port
    db_name = conf.db.name

    # пример: postgresql+asyncpg://user:pass@localhost:5432/db_name
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
