from datetime import datetime
import pydantic

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
    pfp_src: str | None = None

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
    id: int
    user_id: int
    source: str
    top: bool
    likes: int
    dislikes: int
    created_at: datetime
    user: User
    liked: bool | None = None
    disliked: bool | None = None
    score: int
    comment_count: int

    class Config:
        orm_mode = True


# Additional properites to return via API
class Post(PostInDBBase):
    pass


class PostInDB(PostInDBBase):
    pass


# Misc
class Like(pydantic.BaseModel):
    user_id: int
    post_id: int | None = None
    comment_id: int | None = None

    class Config:
        orm_mode = True


### Comment
# Shared properties
class CommentBase(pydantic.BaseModel):
    content: str


# Properties to receive via API on creation
class CommentCreate(CommentBase):
    parent_id: int | None = None
    post_id: int | None = None
    user_id: int


# Properties to receive via API on update
class CommentUpdate(CommentBase):
    pass


class CommentInDBBase(CommentBase):
    attachment_source: str
    dislikes: int
    id: int
    likes: int
    parent_id: int | None = None
    post_id: int
    user_id: int

    class Config:
        orm_mode = True


# Additional properites to return via API
class Comment(CommentInDBBase):
    pass


class CommentInDB(CommentInDBBase):
    pass
