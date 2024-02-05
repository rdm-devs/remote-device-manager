from datetime import datetime
from pydantic import BaseModel
from typing import Optional
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
    os_id: int
    vendor_id: int
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None


class Device(DeviceCreate):
    id: int
    os: DeviceOS
    vendor: DeviceVendor
    is_online: bool
    heartbeat_timestamp: datetime = datetime.now()

    model_config = {"from_attributes": True, "extra": "forbid"}


class DeviceUpdate(DeviceCreate):
    name: Optional[str] = None
    folder_id: Optional[int] = None
    os_id: Optional[int] = None
    vendor_id: Optional[int] = None
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None

    model_config = {"extra": "forbid"}


class DeviceDelete(BaseModel):
    id: int
    msg: str
