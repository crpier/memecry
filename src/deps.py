import functools
import logging
import os
import sys

import fastapi
import fastapi.security
import jose
import jose.jwt
from fastapi import Depends, HTTPException
from sqlmodel import Session, SQLModel

from src import config, models, schema, user_service

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="token")

logger = logging.getLogger()


@functools.lru_cache()
def get_settings():
    settings = config.Settings()  # type: ignore

    # Bootstrapping
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("First admin has id=%s", settings.SUPER_ADMIN_ID)
    try:
        os.mkdir(settings.UPLOAD_STORAGE / "comments")
    except FileExistsError:
        logger.debug("Comment folder exists")
    return settings


@functools.lru_cache()
def get_session():
    # TODO: why can't I use get_settings in Depends?
    settings = get_settings()
    engine = models.get_engine(settings.DB_URL)
    logger.info("Uploading files to %s", settings.UPLOAD_STORAGE)
    SQLModel.metadata.create_all(engine)
    session = functools.partial(Session, engine)
    settings.SUPER_ADMIN_ID = user_service.add_superadmin(session, settings)
    return session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session=Depends(get_session),
    settings: config.Settings = Depends(get_settings),
) -> schema.User:
    credentials_exception = HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    current_user = get_current_user_optional(
        token=token, session=session, settings=settings
    )
    if not current_user:
        raise credentials_exception
    return current_user


def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    session=Depends(get_session),
    settings: config.Settings = Depends(get_settings),
) -> schema.User | None:
    try:
        payload = jose.jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if (res := payload.get("sub")) is None:
            return
        username: str = res
        token_data = schema.TokenData(username=username)
    except jose.JWTError:
        return
    user = user_service.get_user_by_username(session, username=token_data.username)
    if user is None:
        return
    return user
