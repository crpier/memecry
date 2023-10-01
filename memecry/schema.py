from datetime import datetime

from pydantic import BaseModel
from starlette.authentication import SimpleUser

class UserCreate(BaseModel):
    password: str
    username: str

class UserRead(BaseModel, SimpleUser):
    id: int
    username: str
    pass_hash: str
    created_at: datetime
    verified: bool
    pfp_src: str

    class Config:
        from_attributes = True

class PostCreate(BaseModel):
    title: str
    user_id: int
    tags: str

class PostRead(BaseModel):
    id: int
    created_at: datetime
    title: str
    source: str
    user_id: int
    tags: str

    class Config:
        from_attributes = True
