from pydantic import BaseModel
from ..device.schemas import Device

class DeviceGroupBase(BaseModel):
    name: str
    devices: list[Device] | list = []

class DeviceGroupCreate(DeviceGroupBase):
    pass

class DeviceGroup(DeviceGroupBase):
    id: int
    tenant_id: int

    class Config:
        orm_mode = True

class DeviceGroupUpdate(DeviceGroupBase):
    pass

class DeviceGroupDelete(BaseModel):
    id: int
