from pydantic import BaseModel
from typing import Optional
from src.user.schemas import User

class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None

class LoginResponse(BaseModel):
    token: Token
    user: User