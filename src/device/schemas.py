from datetime import datetime
from pydantic import BaseModel
from ..device_group.schemas import DeviceGroup

class DeviceBase(BaseModel):
    name: str
    id_rust: str
    pass_rust: str
    last_screenshot_path: str
    is_online: bool
    heartbeat_timestamp: datetime

class DeviceCreate(DeviceBase):
    device_group: DeviceGroup | None

class Device(DeviceBase):
    id: int

    class Config:
        orm_mode = True
