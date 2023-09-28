from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel): # used as common fields
    email: EmailStr
    group_id: int
    last_login: datetime

class UserCreate(UserBase): # used when creating user
    password: str

class User(UserBase): # used when reading user info
    id: int

    class Config:
        orm_mode = True