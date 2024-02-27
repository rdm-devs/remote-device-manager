from datetime import datetime
from pydantic import BaseModel


class EntityBase(BaseModel):
    pass


class EntityCreate(EntityBase):
    pass


class Entity(EntityCreate):
    id: int

    model_config = {"from_attributes": True}


class EntityUpdate(EntityCreate):
    pass


class EntityDelete(BaseModel):
    id: int
    msg: str
