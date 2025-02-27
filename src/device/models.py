import os
from datetime import datetime, UTC, timedelta
from sqlalchemy import ForeignKey, String, case
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from typing import Optional
from ..database import Base
from ..audit_mixin import AuditMixin
from ..folder.models import Folder
from ..entity.models import Entity


class Device(AuditMixin, Base):
    __tablename__ = "device"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    # is_online: Mapped[bool] = mapped_column(default=True, index=True)
    folder_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("folder.id"), nullable=True
    )
    folder: Mapped[Optional[Folder]] = relationship(Folder, back_populates="devices")
    id_rust: Mapped[Optional[str]] = mapped_column(String(255))
    pass_rust: Mapped[Optional[str]] = mapped_column(String(255))
    last_screenshot_path: Mapped[Optional[str]] = mapped_column(String(255))
    entity_id: Mapped[int] = mapped_column(ForeignKey(Entity.id))
    entity: Mapped[Entity] = relationship(Entity)

    # device metadata attrs:
    MAC_addresses: Mapped[Optional[str]] = mapped_column(String(512))
    local_ips: Mapped[Optional[str]] = mapped_column(
        String(512)
    )  # alternatively: https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.ip_address
    SO_name: Mapped[str] = mapped_column(String(255), index=True)
    SO_version: Mapped[str] = mapped_column(String(255))
    os_kernel_version: Mapped[str] = mapped_column(String(255))
    vendor_name: Mapped[str] = mapped_column(String(255), index=True)
    vendor_model: Mapped[str] = mapped_column(String(255))
    vendor_cores: Mapped[int] = mapped_column()
    vendor_ram_gb: Mapped[int] = mapped_column()
    share_url: Mapped[str] = mapped_column(String(255), nullable=True)
    share_url_expires_at: Mapped[datetime] = mapped_column(nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, unique=True
    )
    time_zone: Mapped[Optional[str]] = mapped_column(String(1000))
    heartbeats: Mapped[Optional[list["src.device.models.Heartbeat"]]] = relationship(
        "src.device.models.Heartbeat"
    )

    @property
    def tags(self):
        return self.entity.tags

    def add_tag(self, tag: "src.tag.models.Tag") -> None:
        self.tags.append(tag)

    @property
    def is_online(self):
        if not self.folder:
            return False
        if not self.folder.tenant:
            return False
        if not self.heartbeats:
            return False

        tenant_heartbeats_interval = self.folder.tenant.settings.heartbeat_s
        # latest_heartbeat_timestamp = self.heartbeats[-1].timestamp
        diff_minutes = (
            datetime.now(UTC) - self.latest_heartbeat_timestamp.astimezone(UTC)
        ).total_seconds() // 60

        max_tolerance_minutes = (
            (tenant_heartbeats_interval // 60)
            * float(os.getenv("MAX_TOLERANCE_HEARTBEATS"))
        ) 
        return diff_minutes <= max_tolerance_minutes

    @property
    def latest_heartbeat_timestamp(self):
        return self.heartbeats[-1].timestamp


class Heartbeat(Base):
    __tablename__ = "heartbeat_logs"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"))
    CPU_load: Mapped[Optional[int]] = mapped_column()
    MEM_load_mb: Mapped[Optional[int]] = mapped_column()
    free_space_mb: Mapped[Optional[int]] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
