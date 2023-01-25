import datetime

import jose
import jose.jwt
import passlib.context

# TODO: this is a dependency
SECRET_KEY = "abcdef"
ALGORITHM = "HS256"

pwd_context = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jose.jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(password, hashed_pass):
    return pwd_context.verify(password, hashed_pass)
