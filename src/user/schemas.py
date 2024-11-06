from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from src.tag.schemas import Tag
from src.tenant.schemas import Tenant, TenantFull

class UserBase(BaseModel):  # used as common fields
    username: EmailStr
    last_login: datetime = datetime.now()
    role_id: Optional[int] = None
    disabled: Optional[bool] = False


class UserCreate(BaseModel):  # used when creating user
    username: EmailStr
    password: str

    model_config = {"extra": "forbid"}


class User(UserBase):  # used when reading user info
    id: int
    entity_id: int
    role_name: str
    model_config = {"from_attributes": True}


class UserUpdate(UserBase):
    username: Optional[EmailStr] = None
    password: Optional[str] = None
    role_id: Optional[int] = None
    tenants: Optional[List[Tenant]] = None
    tags: Optional[List[Tag]] = None
    model_config = {"extra": "ignore"}


class UserDelete(BaseModel):
    id: int
    msg: str
