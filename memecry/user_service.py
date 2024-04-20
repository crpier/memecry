from relax.injection import Injected, injectable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import load_only

import memecry.model
import memecry.schema
import memecry.security


@injectable
async def get_user_by_username(
    username: str,
    fields: list[str] | None = None,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
) -> memecry.schema.UserRead | None:
    async with asession() as session, session.begin():
        stmt = select(memecry.model.User).filter(
            memecry.model.User.username == username
        )
        if fields:
            stmt = stmt.options(
                load_only(*[getattr(memecry.model.User, field) for field in fields]),
            )
        result = await session.execute(stmt)
        user_in_db = result.scalars().one_or_none()
        if user_in_db:
            return memecry.schema.UserRead.model_validate(user_in_db)
        return None


@injectable
async def create_user(
    user: memecry.schema.UserCreate,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
) -> int | None:
    async with asession() as session, session.begin():
        if await get_user_by_username(user.username):
            return None
        new_user = memecry.model.User(
            username=user.username,
            pass_hash=memecry.security.get_password_hash(user.password),
        )
        session.add(new_user)
        await session.commit()
        return new_user.id


@injectable
async def authenticate_user(
    username: str,
    password: str,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
) -> memecry.schema.UserRead | None:
    async with asession() as session, session.begin():
        stmt = select(memecry.model.User).filter(
            memecry.model.User.username == username
        )
        result = await session.execute(stmt)
        user_in_db = result.scalars().one_or_none()
        if user_in_db and memecry.security.verify_password(
            plain_password=password,
            hashed_password=user_in_db.pass_hash,
        ):
            return memecry.schema.UserRead.model_validate(user_in_db)
        return None


@injectable
async def update_user(
    user_id: int,
    user_update: memecry.schema.UserUpdate,
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
) -> None:
    async with asession() as session, session.begin():
        stmt = select(memecry.model.User).filter(memecry.model.User.id == user_id)
        result = await session.execute(stmt)
        user_in_db = result.scalars().one_or_none()
        for key, val in user_update.model_dump().items():
            if val is not None:
                setattr(user_in_db, key, val)
        session.add(user_in_db)
        await session.commit()
