from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):  # used as common fields
    email: EmailStr
    username: str
    last_login: datetime = datetime.now()
    role_id: int | None = None
    disabled: bool | None = False


class UserCreate(BaseModel):  # used when creating user
    email: EmailStr
    username: str
    password: str
    role_id: int

    model_config = {"extra": "forbid"}


class User(UserBase):  # used when reading user info
    id: int
    #hashed_password: str
    model_config = {"from_attributes": True}


class UserUpdate(UserBase):
    username: str | None = None
    password: str | None = None
    email: str | None = None
    role_id: int | None = None

    model_config = {"extra": "forbid"}


class UserDelete(BaseModel):
    id: int
    msg: str
