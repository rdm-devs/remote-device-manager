from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class DeviceBase(BaseModel):
    name: str
    ip_address: str
    mac_address: str
    id_rust: str | None = None
    pass_rust: str | None = None
    last_screenshot_path: str | None = None


class DeviceCreate(DeviceBase):
    folder_id: int
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    os_name: str
    os_version: str
    os_kernel_version: str
    vendor_name: str
    vendor_model: str
    vendor_cores: int
    vendor_ram_gb: int


class Device(DeviceCreate):
    id: int
    is_online: bool
    heartbeat_timestamp: datetime = datetime.now()

    model_config = {"from_attributes": True, "extra": "forbid"}


class DeviceUpdate(DeviceCreate):
    name: Optional[str] = None
    folder_id: Optional[int] = None
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    os_kernel_version: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_model: Optional[str] = None
    vendor_cores: Optional[int] = None
    vendor_ram_gb: Optional[int] = None

    model_config = {"extra": "forbid"}


class DeviceDelete(BaseModel):
    id: int
    msg: str
