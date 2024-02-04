from datetime import datetime
from pydantic import BaseModel
from ..device_os.schemas import DeviceOS
from ..device_vendor.schemas import DeviceVendor

class DeviceBase(BaseModel):
    name: str
    ip_address: str
    mac_address: str
    id_rust: str | None = None
    pass_rust: str | None = None
    last_screenshot_path: str | None = None


class DeviceCreate(DeviceBase):
    folder_id: int


class Device(DeviceCreate):
    id: int
    os: DeviceOS
    vendor: DeviceVendor
    is_online: bool
    heartbeat_timestamp: datetime = datetime.now()

    model_config = {"from_attributes": True}


class DeviceUpdate(DeviceCreate):
    pass

class DeviceDelete(BaseModel):
    id: int
    msg: str
