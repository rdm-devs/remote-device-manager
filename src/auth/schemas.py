from pydantic import BaseModel, HttpUrl
from typing import Optional
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
    token: Token
    device: Optional[Device]
