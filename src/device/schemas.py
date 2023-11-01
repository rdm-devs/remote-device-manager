from datetime import datetime
from pydantic import BaseModel


class DeviceBase(BaseModel):
    name: str
    is_online: bool = True
    heartbeat_timestamp: datetime = datetime.now()
    id_rust: str | None = None
    pass_rust: str | None = None
    last_screenshot_path: str | None = None


class DeviceCreate(DeviceBase):
    device_group_id: int


class Device(DeviceCreate):
    id: int

    model_config = {"from_attributes": True}


class DeviceUpdate(DeviceCreate):
    pass


class DeviceDelete(BaseModel):
    id: int
    msg: str
