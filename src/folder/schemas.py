from pydantic import BaseModel
from ..device.schemas import DeviceList
from typing import Optional, List


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
    devices: List[DeviceList]
    model_config = {"from_attributes": True}


class FolderList(BaseModel):
    id: int
    name: str
    parent_id: Optional[int] = None
    devices: List[DeviceList] = []
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
