from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
from ..database import Base
from ..audit_mixin import AuditMixin
from ..device_group.models import DeviceGroup


class Device(Base, AuditMixin):
    __tablename__ = "device"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True)
    is_online: Mapped[bool] = mapped_column(default=True, index=True)
    heartbeat_timestamp: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )
    device_group_id: Mapped["DeviceGroup"] = mapped_column(
        ForeignKey("device_group.id")
    )
    id_rust: Mapped[Optional[str]]
    pass_rust: Mapped[Optional[str]]
    last_screenshot_path: Mapped[Optional[str]]
