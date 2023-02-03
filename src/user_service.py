import logging
from pydantic import EmailStr
from sqlalchemy.orm import load_only

from sqlmodel import select, Session
from functools import partial
from typing import Callable

from src import models, security, schema

logger = logging.getLogger()


def add_superadmin(session: Callable[[], Session]) -> int:
    with session() as s:
        existing_admin = s.exec(
            select(models.User)
            .options(load_only("id"))
            .where(models.User.username == "admin")
        ).one_or_none()
        if existing_admin and existing_admin.id:
            return existing_admin.id
        new_admin_user = models.User(
            email=EmailStr("admin@example.com"),
            username="admin",
            admin=True,
            pass_hash=security.get_password_hash("kek"),
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
) -> models.User | None:
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
        return user


def get_user_by_username(
    session: Callable[[], Session], username: str
) -> schema.User | None:
    with session() as s:
        res = s.exec(
            select(models.User).where(models.User.username == username)
        ).one_or_none()
        if not res:
            return None
        return schema.User(**res.__dict__)  # type: ignore
