from datetime import datetime
from pydantic import BaseModel


class DeviceVendorBase(BaseModel):
    brand: str
    model: str
    cores: int
    ram_gb: int


class DeviceVendorCreate(DeviceVendorBase):
    pass


class DeviceVendor(DeviceVendorBase):
    id: int

    model_config = {"from_attributes": True}


class DeviceVendorUpdate(DeviceVendorBase):
    pass


class DeviceVendorDelete(BaseModel):
    id: int
    msg: str
