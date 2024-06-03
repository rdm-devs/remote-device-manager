from pydantic import BaseModel
from typing import List, Optional
from src.folder.schemas import Folder, FolderTenantList
from src.tag.schemas import Tag

class TenantBase(BaseModel):
    name: str


class TenantCreate(TenantBase):
    model_config = {"extra": "ignore"}


class Tenant(TenantBase):
    id: int
    entity_id: int
    folders: List[FolderTenantList] = []
    tags: Optional[List[Tag]] = []

    model_config = {"from_attributes": True}


class TenantUpdate(TenantCreate):
    name: Optional[str] = None
    tags: Optional[List[Tag]] = []
    model_config = {"extra": "ignore"}


class TenantDelete(BaseModel):
    id: int
    msg: str

class TenantList(BaseModel):
    id: int
    entity_id: int
    name: str
    folders: List[FolderTenantList] = []
