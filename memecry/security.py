import datetime
import functools
from typing import Any

import jose
import jose.jwt
import passlib.context
import zoneinfo
from relax.injection import Injected, injectable

import memecry.config


@functools.lru_cache
def pwd_context() -> passlib.context.CryptContext:
    return passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")


@injectable
async def create_access_token(
    data: dict, *, config: memecry.config.Config = Injected
) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(tz=zoneinfo.ZoneInfo("UTC")) + datetime.timedelta(
        minutes=100,
    )
    to_encode.update({"exp": expire})
    return jose.jwt.encode(to_encode, config.SECRET_KEY, algorithm="HS256")


def get_password_hash(password: str) -> str:
    return pwd_context().hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context().verify(plain_password, hashed_password)


@injectable
# TODO: don't use any: parse the payload into a dataclass instead
async def decode_payload(
    token: str, *, config: memecry.config.Config = Injected
) -> dict[str, Any]:
    return jose.jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
