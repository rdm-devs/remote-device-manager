from datetime import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
from ..database import Base
from ..audit_mixin import AuditMixin
from ..folder.models import Folder
from ..entity.models import Entity
from ..device_os.models import DeviceOS
from ..device_vendor.models import DeviceVendor

class Device(Base, AuditMixin):
    __tablename__ = "device"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True)
    is_online: Mapped[bool] = mapped_column(default=True, index=True)
    heartbeat_timestamp: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )
    folder_id: Mapped[Folder] = mapped_column(ForeignKey("folder.id"))
    folder: Mapped[Folder] = relationship(Folder, back_populates="devices")
    id_rust: Mapped[Optional[str]]
    pass_rust: Mapped[Optional[str]]
    last_screenshot_path: Mapped[Optional[str]]
    entity_id: Mapped[int] = mapped_column(ForeignKey(Entity.id))

    # device metadata attrs:
    mac_address: Mapped[str] = mapped_column(String(16)) #12  + 4(dots)
    ip_address: Mapped[str] = mapped_column(
        String(15)  # 12  + 3(dots)
    )  # optional: https://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.ip_address
    os_id: Mapped[int] = mapped_column(ForeignKey(DeviceOS.id))
    vendor_id: Mapped[int] = mapped_column(ForeignKey(DeviceVendor.id))
