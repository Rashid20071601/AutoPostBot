from sqlalchemy import Table, Column, Integer, BigInteger, String, MetaData, ForeignKey, REAL

metadata_obj = MetaData()


users = Table(
    "users",
    metadata_obj,
    Column("id", BigInteger, primary_key=True),
    Column("name", String, nullable=True)
)

channels = Table(
    "channels",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("tg_id", BigInteger, unique=True, nullable=False),
    Column("title", String, nullable=False),
    Column("owner_id", BigInteger, ForeignKey("users.id")),
)

mailings = Table(
    "mailings",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("text", String),
    Column("hour", Integer),
    Column("minute", Integer),
    Column("channel_id", Integer),
    Column("enabled", Integer, default=1),
    Column("last_sent", REAL, default=0),
)