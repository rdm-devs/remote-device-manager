from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from ..user.schemas import User


class UserGroupBase(BaseModel):
    name: str


class UserGroupCreate(UserGroupBase):
    pass


class UserGroup(UserGroupBase):
    id: int
    device_group_id: Optional[int] | None
    users: list[User] | list = []

    model_config = {"from_attributes": True}


class UserGroupUpdate(UserGroupBase):
    pass


class UserGroupDelete(BaseModel):
    id: int
    msg: str
