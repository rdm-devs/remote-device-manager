from datetime import datetime
from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int

    model_config = {"from_attributes": True}


class RoleUpdate(RoleBase):
    pass


class RoleDelete(BaseModel):
    id: int
    msg: str
