from pydantic import BaseModel
from typing import Optional

class UserGroupBase(BaseModel):
    name: str


class UserGroupCreate(UserGroupBase):
    pass


class UserGroup(UserGroupBase):
    id: int
    device_group_id: Optional[int] = None
    model_config = {"from_attributes": True}


class UserGroupUpdate(UserGroupBase):
    pass


class UserGroupDelete(BaseModel):
    id: int
    msg: str
