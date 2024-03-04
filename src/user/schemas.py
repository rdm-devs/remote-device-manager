from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):  # used as common fields
    email: EmailStr
    username: str
    last_login: datetime = datetime.now()
    role_id: Optional[int] = None
    disabled: Optional[bool] = False


class UserCreate(BaseModel):  # used when creating user
    email: EmailStr
    username: str
    password: str
    role_id: Optional[int] = None

    model_config = {"extra": "forbid"}


class User(UserBase):  # used when reading user info
    id: int
    #hashed_password: str
    model_config = {"from_attributes": True}


class UserUpdate(UserBase):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    role_id: Optional[int] = None

    model_config = {"extra": "forbid"}


class UserDelete(BaseModel):
    id: int
    msg: str

class UserRole(BaseModel):
    id: int
    role_id: int