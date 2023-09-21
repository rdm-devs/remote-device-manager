from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class UserGroupBase(BaseModel):
    name: str

class UserGroupCreate(UserGroupBase):
    pass

class UserGroup(UserGroupBase):
    id: int
    device_group_id: Optional[int] | None
    user_id: Optional[int] = None

    class Config:
        orm_mode = True

class UserGroupUpdate(BaseModel):
    name: Optional[str] = None
    user_id: Optional[str] = None
    device_group_id: Optional[int] = None

class UserBase(BaseModel): # used as common fields
    email: str
    groups: Optional[list[UserGroup]] = None
    last_login: datetime

class UserCreate(UserBase): # used when creating user
    password: str

class User(UserBase): # used when reading user info
    id: int
    groups: list["UserGroup"] | list = []

    class Config:
        orm_mode = True


class TenantBase(BaseModel):
    name: str

class TenantCreate(TenantBase):
    pass

class Tenant(TenantBase):
    id: int
    groups: list["DeviceGroup"] | list = []

    class Config:
        orm_mode = True


class DeviceGroupBase(BaseModel):
    name: str
    devices: list["Device"] | list = []

class DeviceGroupCreate(DeviceGroupBase):
    pass

class DeviceGroup(DeviceGroupBase):
    id: int
    tenant_id: int | None
    tenant: Tenant | None

    class Config:
        orm_mode = True

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
















