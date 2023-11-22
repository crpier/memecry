import sqlite3

from loguru import logger
from relax.injection import add_injectable
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlite_fts4 import register_functions

from memecry.config import Config
from memecry.model import Base


@logger.catch
async def bootstrap() -> Config:
    config = Config()
    add_injectable(Config, config)

    # ensure media folder exists
    config.MEDIA_UPLOAD_STORAGE.mkdir(parents=True, exist_ok=True)
    # we need a bit of an sync piece on startup lel
    db = sqlite3.connect(config.DB_FILE)

    register_functions(db)
    c = db.cursor()
    c.execute(
        "CREATE VIRTUAL TABLE IF NOT EXISTS posts_data USING fts4(title, content)",
    )

    engine = create_async_engine(f"sqlite+aiosqlite:///{config.DB_FILE}")

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    add_injectable(async_sessionmaker[AsyncSession], async_session)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return config
