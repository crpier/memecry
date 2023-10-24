from relax.injection import Injected, injectable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import load_only

import memecry.security as security
from memecry.model import User
from memecry.schema import UserCreate, UserRead


@injectable
async def get_user_by_username(
    username: str,
    fields: list[str] = [],
    *,
    asession: async_sessionmaker[AsyncSession] = Injected,
) -> UserRead | None:
    async with asession() as session:
        async with session.begin():
            stmt = select(User).filter(User.username == username)
            if fields:
                stmt = stmt.options(
                    load_only(*[getattr(User, field) for field in fields])
                )
            result = await session.execute(stmt)
            user_in_db = result.scalars().one_or_none()
            if user_in_db:
                return UserRead.model_validate(user_in_db)
            else:
                return user_in_db


@injectable
async def create_user(
    user: UserCreate, *, asession: async_sessionmaker[AsyncSession] = Injected
) -> int | None:
    async with asession() as session:
        async with session.begin():
            if await get_user_by_username(user.username):
                return None
            new_user = User(
                username=user.username,
                pass_hash=security.get_password_hash(user.password),
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
) -> UserRead | None:
    async with asession() as session:
        async with session.begin():
            stmt = select(User).filter(User.username == username)
            result = await session.execute(stmt)
            user_in_db = result.scalars().one_or_none()
            if user_in_db and security.verify_password(
                plain_password=password, hashed_password=user_in_db.pass_hash
            ):
                return UserRead.model_validate(user_in_db)
            else:
                return None
