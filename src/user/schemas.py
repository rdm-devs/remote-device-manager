from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):  # used as common fields
    email: EmailStr
    role_id: int
    last_login: datetime = datetime.now()


class UserCreate(UserBase):  # used when creating user
    password: str

    model_config = {"extra": "forbid"}


class User(UserBase):  # used when reading user info
    id: int
    model_config = {"from_attributes": True}


class UserUpdate(UserBase):
    password: str | None = None
    email: str | None = None
    role_id: int | None = None

    model_config = {"extra": "forbid"}


class UserDelete(BaseModel):
    id: int
    msg: str
