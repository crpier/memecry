import logging
from typing import Callable
from fastapi import HTTPException

from pydantic import EmailStr
from sqlalchemy.orm import load_only
from sqlmodel import Session, select

from src import models, schema, security
from src.config import Settings

logger = logging.getLogger()


def add_superadmin(session: Callable[[], Session], settings: Settings) -> int:
    with session() as s:
        existing_admin = s.exec(
            select(models.User)
            .options(load_only("id"))
            .where(models.User.username == settings.SUPER_ADMIN_USERNAME)
        ).one_or_none()
        if existing_admin and existing_admin.id:
            return existing_admin.id
        new_admin_user = models.User(
            email=settings.SUPER_ADMIN_EMAIL,
            username=settings.SUPER_ADMIN_USERNAME,
            admin=True,
            pass_hash=security.get_password_hash(settings.SUPER_ADMIN_PASSWORD),
        )
        s.add(new_admin_user)
        s.commit()
        try:
            res_id = int(new_admin_user.id)  # type: ignore
        except Exception as e:
            logger.error("Error when trying to get id of new user", exc_info=e)
            raise
        return res_id


def authenticate_user(
    session: Callable[[], Session], username: str, password: str
) -> schema.User | None:
    with session() as s:
        res = s.exec(
            select(models.User).where(models.User.username == username)
        ).one_or_none()
        logger.debug("On login found user %s", res)
        if not res:
            return None
        user: models.User = res
        if not security.verify_password(password, user.pass_hash):
            return None
        return schema.User.from_orm(user)


def get_user_by_username(
    session: Callable[[], Session], username: str
) -> schema.User | None:
    with session() as s:
        res = s.exec(
            select(models.User).where(models.User.username == username)
        ).one_or_none()
        if not res:
            return None
        return schema.User.from_orm(res)


SENTINEL_NO_EMAIL = EmailStr("sentinel_no_email@example.com")


def add_user(
    session: Callable[[], Session],
    username: str,
    password: str,
    email: EmailStr | None = None,
):
    if email is None:
        email = SENTINEL_NO_EMAIL

    with session() as s:
        existing_user = get_user_by_username(session=session, username=username)
        if existing_user:
            raise HTTPException(
                status_code=400, detail=f"User with name {username} already exists"
            )
        new_user = models.User(
            email=email,
            username=username,
            pass_hash=security.get_password_hash(password),
        )
        s.add(new_user)
        s.commit()
