from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
from ..database import Base
from ..audit_mixin import AuditMixin
from ..tenant.models import Tenant

class DeviceGroup(Base, AuditMixin):
    __tablename__ = "device_group"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True)
    tenant_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Tenant.id))
    tenant: Mapped[Optional["Tenant"]] = relationship("Tenant", back_populates="device_groups")
