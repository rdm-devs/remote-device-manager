from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from src.tag.schemas import Tag


class DeviceBase(BaseModel):
    name: str
    ip_address: str
    mac_address: str
    id_rust: Optional[str] = None
    pass_rust: Optional[str] = None
    last_screenshot_path: Optional[str] = None
    serialno: Optional[str] = None


class DeviceCreate(DeviceBase):
    folder_id: Optional[int] = None
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
    entity_id: int
    is_online: bool
    heartbeat_timestamp: datetime = datetime.now()
    tags: List[Tag] = []
    share_url: Optional[str] = None
    share_url_expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True, "extra": "ignore"}


class DeviceList(BaseModel):
    id: int
    entity_id: int
    name: str
    is_online: bool
    heartbeat_timestamp: datetime = datetime.now()
    share_url: Optional[str] = None
    share_url_expires_at: Optional[datetime] = None
    serialno: Optional[str] = None


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
    tags: Optional[List[Tag]] = []
    share_url: Optional[str] = None
    share_url_expires_at: Optional[datetime] = None

    model_config = {"extra": "ignore"}


class DeviceDelete(BaseModel):
    id: int
    msg: str


class HeartBeat(BaseModel):
    id_rust: Optional[str] = None
    pass_rust: Optional[str] = None

    model_config = {"extra": "ignore"}


class HeartBeatResponse(BaseModel):
    device_id: int
    timestamp: datetime


class ShareParams(BaseModel):
    expiration_minutes: int


class ShareDeviceURL(BaseModel):
    url: str
