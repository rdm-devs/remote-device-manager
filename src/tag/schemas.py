from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Literal
from src.tag.models import Type


class TagBase(BaseModel):
    name: str
    tenant_id: Optional[int]


class TagCreate(TagBase):
    type: Literal[Type.GLOBAL, Type.USER_CREATED] = Type.USER_CREATED
    model_config = {"extra": "ignore"}


class TagAdminCreate(TagCreate):
    type: Literal[*Type]


class Tag(TagBase):
    id: int
    type: Literal[*Type]

    model_config = {"from_attributes": True}


class TagUpdate(BaseModel):
    name: Optional[str] = None
    tenant_id: Optional[int] = None

    model_config = {"extra": "ignore"}


class TagDelete(BaseModel):
    id: int
    msg: str
