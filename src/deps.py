import functools
import logging
import sys

import fastapi
import fastapi.security
import jose
import jose.jwt
from fastapi import Depends, HTTPException
from sqlite_fts4 import register_functions  # type: ignore
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
    comments_dir = settings.MEDIA_UPLOAD_STORAGE / settings.COMMENT_SUBDIR
    # TODO: this validation should be done in the Settings class
    if comments_dir.exists() and comments_dir.is_dir():
        logger.info("Comments dir already exists")
    elif comments_dir.exists() and not comments_dir.is_dir():
        logger.error("Comments dir is not a directory")
        sys.exit(1)
    elif not comments_dir.exists():
        logger.info("Creating comments dir")
        comments_dir.mkdir(parents=True)
    return settings


@functools.lru_cache()
def get_db_session():
    settings = get_settings()
    engine = models.get_engine(settings.DB_URL)
    logger.info("Uploading files to %s", settings.MEDIA_UPLOAD_STORAGE)
    SQLModel.metadata.create_all(engine)
    # create virtual tables manually
    conn = engine.raw_connection()
    register_functions(conn)
    c = conn.cursor()
    c.execute(
        # TODO: table name comes from config
        "CREATE VIRTUAL TABLE IF NOT EXISTS posts_data USING fts4(title, content)", ()
    )

    session = functools.partial(Session, engine)
    settings.SUPER_ADMIN_ID = user_service.add_superadmin(session, settings)
    return session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session=Depends(get_db_session),
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
    session=Depends(get_db_session),
    settings: config.Settings = Depends(get_settings),
) -> schema.User | None:
    try:
        payload = jose.jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if (res := payload.get("sub")) is None:
            return None
        username: str = res
        token_data = schema.TokenData(username=username)
    except jose.JWTError:
        return None
    user = user_service.get_user_by_username(session, username=token_data.username)
    if user is None:
        return None
    return user
