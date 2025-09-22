# Import libraries
import aiosqlite
from typing import List, Tuple, Optional

# ---------------------- Инициализация БД ---------------------- #
DB = 'mailing.db'

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS mailings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                interval REAL,
                channel_id INTEGER,
                enabled INTEGER DEFAULT 1,
                last_sent REAL DEFAULT 0
            )
        ''')
        await db.commit()


# ---------------------- CRUD ---------------------- #
# Фунция добавления поста
async def add_mailing(text, interval, channel_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            'INSERT INTO mailings (text, interval, channel_id) VALUES (?, ?, ?)',
            (text, interval, channel_id)
            )
        await db.commit()

# Фунция получения всех постов
async def get_mailings() -> List[Tuple]:
    async with aiosqlite.connect(DB) as db:
        async with db.execute('SELECT * FROM mailings') as cursor:
            return await cursor.fetchall()

# Фунция получения конкректного поста
async def get_mailing(mailing_id: int) -> Optional[Tuple]:
    async with aiosqlite.connect(DB) as db:
        async with db.execute('SELECT * FROM mailings WHERE id=?', (mailing_id,)) as cursor:
            return await cursor.fetchone()

# Фунция обновления поста
async def update_mailing(
        mailing_id: int,
        text: Optional[str] = None,
        interval: Optional[int] = None,
        enabled: Optional[int] = None
    ) -> None:
    async with aiosqlite.connect(DB) as db:
        if text is not None:
            await db.execute('UPDATE mailings SET text=? WHERE id=?', (text, mailing_id))
        if interval is not None:
            await db.execute('UPDATE mailings SET interval=? WHERE id=?', (interval, mailing_id))
        if enabled is not None:
            await db.execute('UPDATE mailings SET enabled=? WHERE id=?', (enabled, mailing_id))
        await db.commit()

# Функция удаления поста
async def delete_mailing(mailing_id: int) -> None:
    async with aiosqlite.connect(DB) as db:
        await db.execute('DELETE FROM mailings WHERE id=?', (mailing_id,))
        await db.commit()

# Функция обновления времени последней отправки
async def update_last_sent(mailing_id: int, timestamp: int) -> None:
    async with aiosqlite.connect(DB) as db:
        await db.execute('UPDATE mailings SET last_sent=? WHERE id=?', (timestamp, mailing_id))
        await db.commit()