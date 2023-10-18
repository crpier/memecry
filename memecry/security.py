import datetime
import functools

import jose
import jose.jwt
import passlib.context
from yahgl_py.injection import Injected, injectable

from memecry.config import Config


@functools.lru_cache
def pwd_context():
    return passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")


@injectable
async def create_access_token(data: dict, *, config: Config = Injected):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=100)
    to_encode.update({"exp": expire})
    return jose.jwt.encode(to_encode, config.SECRET_KEY, algorithm="HS256")


def get_password_hash(password: str):
    return pwd_context().hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context().verify(plain_password, hashed_password)

@injectable
async def decode_payload(token: str, *, config: Config = Injected):
    return jose.jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
