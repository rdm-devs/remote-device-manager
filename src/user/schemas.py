from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel): # used as common fields
    email: str
    group_id: int
    last_login: datetime

class UserCreate(UserBase): # used when creating user
    password: str

class User(UserBase): # used when reading user info
    id: int

    class Config:
        orm_mode = True