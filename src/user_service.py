import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from src import models, security, schema

logger = logging.getLogger()


def add_superadmin(s: Session) -> int:
    with s:
        existing_admin = s.execute(
            select(models.User.id).where(models.User.username == "admin")
        ).one_or_none()
        if existing_admin is not None:
            return existing_admin.id
        new_admin_user = models.User(
            email="admin@example.com", username="admin", admin=True, pass_hash=security.get_password_hash("kek")
        )
        s.add(new_admin_user)
        s.commit()
        try:
            res_id = int(new_admin_user.id)  # type: ignore
        except Exception as e:
            logger.error("Error when trying to get id of new user", exc_info=e)
            raise
        return res_id


def authenticate_user(s: Session, username: str, password: str) -> models.User | None:
    with s:
        res = s.execute(
            select(models.User).where(models.User.username == username)
        ).one_or_none()
        logger.debug("On login found user %s", res)
        if not res:
            return None
        user: models.User = res[0]
        if not security.verify_password(password, user.pass_hash):
            return None
        return user


def get_user_by_username(s: Session, username: str) -> schema.User | None:
    with s:
        res = s.execute(
            select(models.User).where(models.User.username == username)
        ).one_or_none()
        if not res:
            return None
        return schema.User(**res[0].__dict__) # type: ignore
