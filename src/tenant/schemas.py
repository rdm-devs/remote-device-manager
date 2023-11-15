from pydantic import BaseModel
from ..device_group.schemas import DeviceGroup


class TenantBase(BaseModel):
    name: str


class TenantCreate(TenantBase):
    model_config = {"extra": "forbid"}


class Tenant(TenantBase):
    id: int
    device_groups: list[DeviceGroup] = []

    model_config = {"from_attributes": True}


class TenantUpdate(TenantCreate):
    model_config = {"extra": "forbid"}


class TenantDelete(BaseModel):
    id: int
    msg: str
