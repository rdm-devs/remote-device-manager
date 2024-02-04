from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped
from ..database import Base
from ..audit_mixin import AuditMixin


class DeviceOS(Base, AuditMixin):
    __tablename__ = "device_os"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True)
    version: Mapped[str] = mapped_column()
    kernel_version: Mapped[str] = mapped_column()

    __table_args__ = (UniqueConstraint("name", "version", name="_name_version_uc"),)
