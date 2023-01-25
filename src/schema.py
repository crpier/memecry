import pydantic
import enum

### User

# Shared properties
class UserBase(pydantic.BaseModel):
    username: str
    email: str | None = None
    admin: bool | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: str
    admin: bool = False
    verified: bool = False
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str | None = None
    email: str | None = None


class UserInDBBase(UserBase):
    id: int
    achievements: dict[str, str]
    verified: bool
    banned: bool
    admin: bool

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


### Login
class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


class TokenData(pydantic.BaseModel):
    username: str


### Post
# Shared properties
class PostBase(pydantic.BaseModel):
    title: str


# Properties to receive via API on creation
class PostCreate(PostBase):
    user_id: int
    top: bool = False


# Properties to receive via API on update
class PostUpdate(PostBase):
    pass


class PostInDBBase(PostBase):
    user_id: int
    source: int
    top: bool
    likes: int
    dislikes: int
    user_id: int


# Additional properites to return via API
class Post(PostInDBBase):
    pass


class PostInDB(PostInDBBase):
    pass
