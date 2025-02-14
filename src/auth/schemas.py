from pydantic import BaseModel, HttpUrl, EmailStr
from typing import Optional
from datetime import datetime
from src.user.schemas import User
from src.device.schemas import Device

class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None


class ConnectionToken(BaseModel):
    id: int  # device_id
    id_rust: str
    pass_rust: str

    model_config = {"from_attributes": True, "extra": "ignore"}


class ConnectionUrl(BaseModel):
    url: HttpUrl

class LoginData(BaseModel):
    access_token: str
    refresh_token: str
    device: Optional[Device]


class AuthRefreshToken(BaseModel):
    id: int
    user_id: int
    serial_number: str
    refresh_token: str
    expires_at: datetime
    valid: bool

    model_config = {"from_attributes": True}

class DeviceLoginData(BaseModel):
    refresh_token: str


class ForgotPasswordData(BaseModel):
    email: EmailStr


class ForgotPasswordEmailSent(BaseModel):
    msg: str
    url: Optional[str]

class PasswordUpdateData(BaseModel):
    new_password: str

class PasswordUpdated(BaseModel):
    msg: str