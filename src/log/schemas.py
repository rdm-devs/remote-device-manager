from datetime import datetime
from pydantic import BaseModel
from .models import LogActionEnum

class LogEntryBase(BaseModel):
    old_values: str | None = None
    new_values: str | None = None
    timestamp: datetime = datetime.now()


class LogEntryCreate(LogEntryBase):
    entity_id: int
    user_id: int
    action: LogActionEnum

class LogEntry(LogEntryCreate):
    id: int

    model_config = {"from_attributes": True}


class LogEntryUpdate(LogEntryCreate):
    pass


class LogEntryDelete(BaseModel):
    id: int
    msg: str
