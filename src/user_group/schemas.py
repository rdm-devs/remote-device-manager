from pydantic import BaseModel
from typing import Optional


class UserGroupBase(BaseModel):
    name: str


class UserGroupCreate(UserGroupBase):
    device_group_id: Optional[int] = None
    model_config = {"extra": "forbid"}


class UserGroup(UserGroupBase):
    id: int
    device_group_id: Optional[int] = None
    model_config = {"from_attributes": True}


class UserGroupUpdate(UserGroupCreate):
    name: Optional[str]
    model_config = {"extra": "forbid"}


class UserGroupDelete(BaseModel):
    id: int
    msg: str
