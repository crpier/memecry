from pydantic import BaseModel

class UserCreate(BaseModel):
    password: str
    username: str

class UserRead(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
