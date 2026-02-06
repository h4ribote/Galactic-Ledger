from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    id: int

class User(UserBase):
    id: int

    class Config:
        from_attributes = True
