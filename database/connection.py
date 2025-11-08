# ========================= Импорт библиотек ========================= #
from typing import Any


# ========================= Формирование строки подключения ========================= #
def get_db_url(conf: Any) -> str:
    """
    Формирует строку подключения к PostgreSQL с asyncpg-драйвером.
    Использует значения из конфигурации (объект Config).
    """
    user = conf.db.user
    password = conf.db.password
    host = conf.db.host
    port = conf.db.port
    db_name = conf.db.name

    # ⚠️ Оборачиваем пароль в URL-кодирование на случай специальных символов
    from urllib.parse import quote_plus
    password_safe = quote_plus(password)

    # Пример: postgresql+asyncpg://user:pass@localhost:5432/db_name
    url = f"postgresql+asyncpg://{user}:{password_safe}@{host}:{port}/{db_name}"
    return url
