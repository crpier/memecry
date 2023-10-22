import sqlite3
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlite_fts4 import register_functions

from memecry.model import Base
from memecry.config import Config
from relax.injection import add_injectable


async def bootstrap():
    config = Config()
    add_injectable(Config, config)

    # ensure media folder exists
    config.MEDIA_UPLOAD_STORAGE.mkdir(parents=True, exist_ok=True)

    # we need a bit of an sync piece on startup lel
    assert config.DB_URL.path

    # strip the leading slash as for sqlite "/dev.db" means "./dev.db"
    db_path = config.DB_URL.path[1:]
    db = sqlite3.connect(db_path)
    register_functions(db)
    c = db.cursor()
    # TODO: set table name in config
    c.execute(
        f"CREATE VIRTUAL TABLE IF NOT EXISTS {config.SEARCH_TABLE} USING fts4(title, content)"
    )

    engine = create_async_engine(str(config.DB_URL))

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    add_injectable(async_sessionmaker[AsyncSession], async_session)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return config
