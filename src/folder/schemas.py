from pydantic import BaseModel
from typing import Optional, List
from src.device.schemas import Device, DeviceList
from src.tag.schemas import Tag


class SubfolderList(BaseModel):
    id: int
    name: str
    parent_id: int


class FolderBase(BaseModel):
    name: str
    tenant_id: int
    subfolders: List["Folder"] = []


class Folder(FolderBase):
    id: int
    parent_id: Optional[int] = None
    devices: List[Device]
    model_config = {"from_attributes": True}


class FolderList(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    #tenant_id: Optional[int] = None
    tags: List[Tag] = []
    devices: List[Device] = []
    subfolders: List["FolderList"] = []


class FolderTenantList(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None


class FolderCreate(FolderBase):
    parent_id: Optional[int] = None


class FolderUpdate(FolderCreate):
    name: Optional[str] = None
    tenant_id: Optional[int] = None
    parent_id: Optional[int] = None


class FolderDelete(BaseModel):
    id: int
    msg: str
