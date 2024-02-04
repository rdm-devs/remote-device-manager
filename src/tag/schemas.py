from datetime import datetime
from pydantic import BaseModel


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass

class Tag(TagCreate):
    id: int

    model_config = {"from_attributes": True}


class TagUpdate(TagCreate):
    pass


class TagDelete(BaseModel):
    id: int
    msg: str
