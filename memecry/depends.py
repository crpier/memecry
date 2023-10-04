import sqlite3
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlite_fts4 import register_functions

from memecry.model import Base
from yahgl_py.injection import add_injectable


async def bootstrap():
    db_dsn = "sqlite+aiosqlite:///dev.db"

    # we need a bit of an async piece on startup lel
    db = sqlite3.connect("dev.db")
    register_functions(db)
    c = db.cursor()
    # TODO: set table name in config
    c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS posts_data USING fts4(title, content)")

    engine = create_async_engine(db_dsn)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    add_injectable(async_sessionmaker[AsyncSession], async_session)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
