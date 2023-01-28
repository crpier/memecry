import os
import fastapi
import fastapi.security
import jose
import jose.jwt
from fastapi import Depends, HTTPException
import logging
import sys

import functools
from src import db, schema, user_service, config, models

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="token")


@functools.lru_cache()
def get_settings():
    settings = config.Settings()
    settings.SUPER_ADMIN_ID = user_service.add_superadmin(get_session())

    # Bootstrapping
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("First admin has id=%s", settings.SUPER_ADMIN_ID)
    logger.info("Uploading files to %s", settings.UPLOAD_STORAGE)
    os.mkdir(settings.UPLOAD_STORAGE / "comments")
    return settings


@functools.lru_cache()
def get_session():
    engine = models.get_engine()
    models.Base.metadata.create_all(engine)
    session = models.get_sessionmaker(engine)()
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
    try:
        payload = jose.jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if (res := payload.get("sub")) is None:
            raise credentials_exception
        username: str = res
        token_data = schema.TokenData(username=username)
    except jose.JWTError:
        raise credentials_exception
    user = user_service.get_user_by_username(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
