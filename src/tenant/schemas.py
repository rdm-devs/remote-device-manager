from pydantic import BaseModel
from ..device_group.schemas import DeviceGroup

class TenantBase(BaseModel):
    name: str

class TenantCreate(TenantBase):
    groups: list[DeviceGroup] | list = []

class Tenant(TenantBase):
    id: int
    groups: list[DeviceGroup] | list

    class Config:
        orm_mode = True

class TenantUpdate(TenantCreate):
    pass

class TenantDelete(BaseModel):
    id: int
    msg: str