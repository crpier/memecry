import pydantic


class User(pydantic.BaseModel):
    username: str
    email: str | None = None
    admin: bool | None = None


class UserInDB(User):
    hashed_password: str


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class TokenData(pydantic.BaseModel):
    username: str
