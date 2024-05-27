from pydantic import BaseModel
from typing import Optional, List
from src.device.schemas import Device, DeviceList
from src.tag.schemas import Tag


class FolderTenantList(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None


class FolderBase(BaseModel):
    name: str
    tenant_id: int
    subfolders: List["Folder"] = []


# class Folder(FolderBase):
#     id: int
#     parent_id: Optional[int] = None
#     devices: List[Device]
#     model_config = {"from_attributes": True}


class Folder(BaseModel):
    id: int
    name: str
    entity_id: int
    parent_id: Optional[int] = None
    tenant_id: Optional[int] = None
    tags: List[Tag] = []
    devices: List[Device] = []
    subfolders: List["Folder"] = []
    model_config = {"from_attributes": True}


class FolderCreate(FolderBase):
    parent_id: Optional[int] = None


class FolderUpdate(FolderBase):
    name: Optional[str] = None
    tenant_id: Optional[int] = None
    parent_id: Optional[int] = None
    tags: Optional[List[Tag]] = None
    devices: Optional[List[Device]] = None
    subfolders: Optional[List["Folder"]] = None
    model_config = {"extra": "ignore"}


class FolderDelete(BaseModel):
    id: int
    msg: str
