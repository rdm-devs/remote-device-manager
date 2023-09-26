from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
from ..database import Base

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    last_login: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    group_id: Mapped[Optional[int] | None] = mapped_column(ForeignKey("user_group.id"))
    group: Mapped[Optional["UserGroup"]] = relationship("UserGroup", backref="users", foreign_keys=[group_id])