from pydantic import BaseModel
from typing import List, Optional
from src.folder.schemas import Folder, FolderTenantList
from src.user.schemas import UserRole
from src.tag.schemas import Tag

class TenantBase(BaseModel):
    name: str


class TenantCreate(TenantBase):
    model_config = {"extra": "forbid"}


class Tenant(TenantBase):
    id: int
    folders: List[FolderTenantList] = []
    tags: Optional[List[Tag]] = []

    model_config = {"from_attributes": True}


class TenantUpdate(TenantCreate):
    model_config = {"extra": "forbid"}


class TenantDelete(BaseModel):
    id: int
    msg: str

class TenantList(BaseModel):
    id: int
    name: str
    #users: List[UserRole] = []
    folders: List[FolderTenantList] = []
