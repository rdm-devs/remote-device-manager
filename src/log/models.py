import enum
from datetime import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
from ..database import Base
from ..user.models import User
from ..entity.models import Entity


class LogActionEnum(enum.Enum):
    CREATE = enum.auto()
    UPDATE = enum.auto()
    DELETE = enum.auto()


class LogEntry(Base):
    __tablename__ = "log"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey(Entity.id), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id), index=True)
    action: Mapped[LogActionEnum] = mapped_column()
    old_values: Mapped[Optional[str]] = mapped_column()
    new_values: Mapped[Optional[str]] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )
