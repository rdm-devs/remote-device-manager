from datetime import datetime
from pydantic import BaseModel


class DeviceOSBase(BaseModel):
    name: str
    version: str
    kernel_version: str


class DeviceOSCreate(DeviceOSBase):
    pass


class DeviceOS(DeviceOSBase):
    id: int

    model_config = {"from_attributes": True}


class DeviceOSUpdate(DeviceOSBase):
    pass


class DeviceOSDelete(BaseModel):
    id: int
    msg: str
