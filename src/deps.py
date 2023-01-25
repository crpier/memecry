import fastapi
import fastapi.security
import jose
import jose.jwt
from fastapi import Depends, HTTPException

from src import db, schema, security, user_service

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(tokenUrl="token")


def get_session():
    return db.session


async def get_current_user(
    token: str = Depends(oauth2_scheme), session=Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jose.jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
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
