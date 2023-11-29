from typing import Optional
from pydantic import BaseModel
from ..device.schemas import Device


class DeviceGroupBase(BaseModel):
    name: str
    tenant_id: Optional[int] = None


class DeviceGroupCreate(DeviceGroupBase):
    devices: Optional[list[Device]] = []


class DeviceGroup(DeviceGroupBase):
    id: int
    devices: list[Device]
    model_config = {"from_attributes": True}


class DeviceGroupUpdate(DeviceGroupCreate):
    pass


class DeviceGroupDelete(BaseModel):
    id: int
    msg: str
