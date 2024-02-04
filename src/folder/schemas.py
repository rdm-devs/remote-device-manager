from pydantic import BaseModel
from ..device.schemas import Device


class FolderBase(BaseModel):
    name: str
    tenant_id: int
    subfolders: list["Folder"] = []


class Folder(FolderBase):
    id: int
    parent_id: int | None = None
    devices: list[Device]
    model_config = {"from_attributes": True}


class FolderCreate(FolderBase):
    parent_id: int | None = None


class FolderUpdate(FolderCreate):
    pass


class FolderDelete(BaseModel):
    id: int
    msg: str
