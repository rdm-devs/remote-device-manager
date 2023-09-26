from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
from ..base import Base
from ..audit_mixin import AuditMixin
from ..device_group.models import DeviceGroup

class Device(Base, AuditMixin):
    __tablename__ = "device"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True)
    id_rust: Mapped[str] = mapped_column()
    pass_rust: Mapped[str] = mapped_column()
    last_screenshot_path: Mapped[str] = mapped_column()
    is_online: Mapped[bool] = mapped_column(default=True, index=True)
    heartbeat_timestamp: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    device_group_id: Mapped[Optional["DeviceGroup"] | None] = mapped_column(ForeignKey("device_group.id")) 
    #device_group: Mapped[Optional["DeviceGroup"] | None] = relationship("DeviceGroup", back_populates="devices")