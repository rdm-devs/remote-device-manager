from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from src.tag.schemas import Tag


class DeviceBase(BaseModel):
    name: str
    local_ips: str
    MAC_addresses: str
    id_rust: Optional[str] = None
    pass_rust: Optional[str] = None
    last_screenshot_path: Optional[str] = None
    serial_number: Optional[str] = None
    time_zone: Optional[str] = None


class DeviceCreate(DeviceBase):
    folder_id: Optional[int] = None
    MAC_addresses: Optional[str] = None
    local_ips: Optional[str] = None
    time_zone: Optional[str] = None
    SO_name: str
    SO_version: str
    os_kernel_version: str
    vendor_name: str
    vendor_model: str
    vendor_cores: int
    vendor_ram_gb: int


class Device(DeviceCreate):
    id: int
    entity_id: int
    is_online: bool
    #heartbeat_timestamp: datetime
    tags: List[Tag] = []
    share_url: Optional[str] = None
    share_url_expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True, "extra": "ignore"}


class DeviceList(BaseModel):
    id: int
    entity_id: int
    name: str
    is_online: bool
    tags: List[Tag] = []
    heartbeat_timestamp: Optional[datetime] = None
    share_url: Optional[str] = None
    share_url_expires_at: Optional[datetime] = None
    serial_number: Optional[str] = None


class DeviceUpdate(DeviceCreate):
    name: Optional[str] = None
    folder_id: Optional[int] = None
    MAC_addresses: Optional[str] = None
    local_ips: Optional[str] = None
    SO_name: Optional[str] = None
    SO_version: Optional[str] = None
    os_kernel_version: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_model: Optional[str] = None
    vendor_cores: Optional[int] = None
    vendor_ram_gb: Optional[int] = None
    tags: Optional[List[Tag]] = []
    share_url: Optional[str] = None
    share_url_expires_at: Optional[datetime] = None
    time_zone: Optional[str] = None

    model_config = {"extra": "ignore"}


class DeviceDelete(BaseModel):
    id: int
    msg: str


class HeartBeat(BaseModel):
    id_rust: Optional[str] = None
    pass_rust: Optional[str] = None
    CPU_load: Optional[int] = None
    MEM_load_mb: Optional[int] = None
    free_space_mb: Optional[int] = None

    model_config = {"extra": "ignore"}


class HeartBeatResponse(BaseModel):
    device_id: int
    timestamp: datetime
    heartbeat_s: int # seconds between messages


class ShareParams(BaseModel):
    expiration_minutes: int


class ShareDeviceURL(BaseModel):
    url: str
