from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
from ..database import Base
from ..user_group.models import user_and_groups_table


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    last_login: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )
    user_groups: Mapped[list["src.user_group.models.UserGroup"]] = relationship(
        secondary=user_and_groups_table, back_populates="users"
    )
