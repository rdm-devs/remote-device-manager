from pydantic import BaseModel, PositiveInt
from typing import List, Optional
from src.folder.schemas import Folder, FolderTenantList
from src.tag.schemas import Tag


class TenantBase(BaseModel):
    name: str


class TenantCreate(TenantBase):
    tags: Optional[List[Tag]] = None
    model_config = {"extra": "ignore"}


class Tenant(TenantBase):
    id: int
    entity_id: int
    folders: List[FolderTenantList] = []
    tags: Optional[List[Tag]] = []

    model_config = {"from_attributes": True}


class TenantUpdate(TenantCreate):
    name: Optional[str] = None
    tags: Optional[List[Tag]] = None
    model_config = {"extra": "ignore"}


class TenantDelete(BaseModel):
    id: int
    msg: str


class TenantFull(Tenant):
    folders: List[Folder] = []


class TenantSettings(BaseModel):
    heartbeat_s: PositiveInt

    model_config = {"extra": "ignore"}


class TenantSettingsCreate(TenantSettings):
    pass


class TenantSettingsUpdate(TenantSettings):
    pass
