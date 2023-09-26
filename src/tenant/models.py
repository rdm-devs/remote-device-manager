from sqlalchemy.orm import relationship, mapped_column, Mapped
from ..database import Base
from ..audit_mixin import AuditMixin


class Tenant(Base, AuditMixin):
    __tablename__ = "tenant"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True)
    device_groups: Mapped[list["DeviceGroup"]] = relationship("DeviceGroup", back_populates="tenant")
