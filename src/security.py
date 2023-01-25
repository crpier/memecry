import datetime

import jose
import jose.jwt
import passlib.context

from src import config

pwd_context = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, settings: config.Settings):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=100)
    to_encode.update({"exp": expire})
    return jose.jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(password, hashed_pass):
    return pwd_context.verify(password, hashed_pass)
