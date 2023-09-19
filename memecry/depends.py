from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from memecry.model import Base
from yahgl_py.injection import add_injectable



async def bootstrap():
    engine = create_async_engine(
        "sqlite+aiosqlite:///dev.db",
        echo=True,
    )

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    add_injectable(async_sessionmaker[AsyncSession], async_session)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
