from datetime import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
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
    is_online: Mapped[bool] = mapped_column(default=True, index=True)
    heartbeat_timestamp: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )
    folder_id: Mapped[Optional[int]] = mapped_column(ForeignKey("folder.id"), nullable=True)
    folder: Mapped[Optional[Folder]] = relationship(Folder, back_populates="devices")
    id_rust: Mapped[Optional[str]] = mapped_column(String(255))
    pass_rust: Mapped[Optional[str]] = mapped_column(String(255))
    last_screenshot_path: Mapped[Optional[str]] = mapped_column(String(255))
    entity_id: Mapped[int] = mapped_column(ForeignKey(Entity.id))
    entity: Mapped[Entity] = relationship(Entity)

    # device metadata attrs:
    mac_address: Mapped[Optional[str]] = mapped_column(String(17))
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(15)
    )  # alternatively: https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.ip_address
    os_name: Mapped[str] = mapped_column(String(255), index=True)
    os_version: Mapped[str] = mapped_column(String(255))
    os_kernel_version: Mapped[str] = mapped_column(String(255))
    vendor_name: Mapped[str] = mapped_column(String(255), index=True)
    vendor_model: Mapped[str] = mapped_column(String(255))
    vendor_cores: Mapped[int] = mapped_column()
    vendor_ram_gb: Mapped[int] = mapped_column()
    share_url: Mapped[str] = mapped_column(String(255), nullable=True)
    share_url_expires_at: Mapped[datetime] = mapped_column(nullable=True)
    serialno: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)

    @property
    def tags(self):
        return self.entity.tags

    def add_tag(self, tag: "src.tag.models.Tag") -> None:
        self.tags.append(tag)


class Heartbeat(Base):
    __tablename__ = "heartbeat_logs"
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"))
    CPU_load: Mapped[Optional[int]] = mapped_column()
    MEM_load_mb: Mapped[Optional[int]] = mapped_column()
    free_space_mb: Mapped[Optional[int]] = mapped_column()
    timestamp: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )
