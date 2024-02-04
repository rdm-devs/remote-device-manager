from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from ..database import Base
from ..audit_mixin import AuditMixin


class DeviceVendor(Base, AuditMixin):
    __tablename__ = "device_vendor"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    brand: Mapped[str] = mapped_column(index=True, unique=True)
    model: Mapped[str] = mapped_column()
    cores: Mapped[int] = mapped_column()
    ram_gb: Mapped[int] = mapped_column()
    devices: Mapped["Device"] = relationship("Device", back_populates="vendor")
