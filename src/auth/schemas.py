from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None
