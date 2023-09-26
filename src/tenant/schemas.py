from pydantic import BaseModel
from ..device_group.schemas import DeviceGroup

class TenantBase(BaseModel):
    name: str

class TenantCreate(TenantBase):
    pass

class Tenant(TenantBase):
    id: int
    groups: list[DeviceGroup] | list = []

    class Config:
        orm_mode = True
