from sqlalchemy import ForeignKey, Table, Column, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
from ..database import Base
from ..audit_mixin import AuditMixin
from ..device_group.models import DeviceGroup


user_and_groups_table = Table(
    "users_and_groups",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("group_id", ForeignKey("user_group.id"), primary_key=True),
    Column("created_at",  DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
)


class UserGroup(Base, AuditMixin):
    __tablename__ = "user_group"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True)
    device_group_id: Mapped[Optional[int]] = mapped_column(ForeignKey(DeviceGroup.id))
    users: Mapped[list["src.user.models.User"]] = relationship(
        secondary=user_and_groups_table, back_populates="user_groups"
    )
