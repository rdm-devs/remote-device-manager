from pydantic import BaseModel
from typing import List
from ..folder.schemas import Folder

class TenantBase(BaseModel):
    name: str


class TenantCreate(TenantBase):
    model_config = {"extra": "forbid"}


class Tenant(TenantBase):
    id: int
    folders: List[Folder] = []

    model_config = {"from_attributes": True}


class TenantUpdate(TenantCreate):
    model_config = {"extra": "forbid"}


class TenantDelete(BaseModel):
    id: int
    msg: str
