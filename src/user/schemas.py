from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class UserBase(BaseModel):  # used as common fields
    email: EmailStr
    group_id: int
    last_login: datetime


class UserCreate(UserBase):  # used when creating user
    password: str


class User(UserBase):  # used when reading user info
    id: int

    model_config = {"from_attributes": True}


class UserUpdate(UserCreate):
    pass


class UserDelete(BaseModel):
    id: int
    msg: str
