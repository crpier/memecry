import datetime

import jose
import jose.jwt
import passlib.context

pwd_context = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=100)
    to_encode.update({"exp": expire})
    return jose.jwt.encode(to_encode, "abcd", algorithm="HS256")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    print(plain_password)
    print(hashed_password)
    return pwd_context.verify(plain_password, hashed_password)
