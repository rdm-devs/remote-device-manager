from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):  # used as common fields
    email: EmailStr
    last_login: datetime = datetime.now()


class UserCreate(UserBase):  # used when creating user
    password: str

    model_config = {"extra": "forbid"}


class User(UserBase):  # used when reading user info
    id: int
    model_config = {"from_attributes": True}


class UserUpdate(UserBase):
    password: Optional[str] = None

    model_config = {"extra": "forbid"}


class UserDelete(BaseModel):
    id: int
    msg: str
