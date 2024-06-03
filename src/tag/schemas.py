from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class TagBase(BaseModel):
    name: str
    tenant_id: int


class TagCreate(TagBase):
    model_config = {"extra": "ignore"}

class Tag(TagCreate):
    id: int

    model_config = {"from_attributes": True}


class TagUpdate(BaseModel):
    name: Optional[str] = None
    tenant_id: Optional[int] = None

    model_config = {"extra": "ignore"}

class TagDelete(BaseModel):
    id: int
    msg: str
