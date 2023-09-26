from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import Optional
from ..database import Base
from ..audit_mixin import AuditMixin
from ..device_group.models import DeviceGroup

class UserGroup(Base, AuditMixin):
    __tablename__ = "user_group"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True)
    device_group_id: Mapped[Optional[int] | None] = mapped_column(ForeignKey(DeviceGroup.id))
    #users: Mapped[Optional[list["User"]]] = relationship("User") # not working
