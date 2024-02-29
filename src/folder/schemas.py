from pydantic import BaseModel
from ..device.schemas import Device
from typing import Optional, List

class FolderBase(BaseModel):
    name: str
    tenant_id: int
    subfolders: List["Folder"] = []


class Folder(FolderBase):
    id: int
    parent_id: Optional[int] = None
    devices: List[Device]
    model_config = {"from_attributes": True}


class FolderCreate(FolderBase):
    parent_id: Optional[int] = None


class FolderUpdate(FolderCreate):
    name: Optional[str] = None
    tenant_id: Optional[int] = None
    parent_id: Optional[int]  = None


class FolderDelete(BaseModel):
    id: int
    msg: str
