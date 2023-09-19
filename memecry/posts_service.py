import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import selectinload

from memecry.model import Base, User, Post

async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add_all(
                [
                    User(
                        posts=[
                            Post(title="b1", source="aaa"),
                            Post(title="post2", source="aaa"),
                        ],
                        email="a1",
                        username="cris",
                        pass_hash="123456",
                    ),
                    User(posts=[], email="a2", username="cris", pass_hash="123456"),
                    User(
                        posts=[
                            Post(title="Post3", source="aaa"),
                            Post(title="post4", source="aaa"),
                        ],
                        email="a3",
                        username="cris",
                        pass_hash="123456",
                    ),
                ]
            )


async def select_and_update_objects(
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    async with async_session() as session:
        stmt = select(User).options(selectinload(User.posts))

        result = await session.execute(stmt)

        for a1 in result.scalars():
            print(a1)
            print(f"created at: {a1.created_at}")
            for b1 in a1.posts:
                print(b1)

        result = await session.execute(select(User).order_by(User.id).limit(1))

        a1 = result.scalars().one()

        a1.email = "a1newemail"

        await session.commit()

        # access attribute subsequent to commit; this is what
        # expire_on_commit=False allows
        print(a1.email)

        # alternatively, AsyncAttrs may be used to access any attribute
        # as an awaitable (new in 2.0.13)
        for b1 in await a1.awaitable_attrs.posts:
            print(b1)


async def async_main() -> None:
    engine = create_async_engine(
        "sqlite+aiosqlite:///dev.db",
        echo=True,
    )

    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await insert_objects(async_session)
    await select_and_update_objects(async_session)

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    await engine.dispose()


asyncio.run(async_main())
