from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
from .database import Base
from .audit_mixin import AuditMixin

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    last_login: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    group_id: Mapped[Optional[int] | None] = mapped_column(ForeignKey("user_group.id"))
    #group: Mapped[Optional["UserGroup"]] = relationship("UserGroup", back_populates="users", foreign_keys=[group_id]) # not working

class UserGroup(Base, AuditMixin):
    __tablename__ = "user_group"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    device_group_id: Mapped[Optional[int] | None] = mapped_column(ForeignKey("device_group.id"))
    #users: Mapped[list["User"]] = relationship("User", back_populates="group") # not working

class DeviceGroup(Base, AuditMixin):
    __tablename__ = "device_group"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    devices: Mapped[Optional[list["Device"]]] = relationship("Device", back_populates="device_groups")
    tenant_id: Mapped[Optional[int] | None] = mapped_column(ForeignKey("tenant.id"))
    tenant: Mapped[Optional["Tenant"]] = relationship("Tenant", back_populates="device_groups")

class Device(Base, AuditMixin):
    __tablename__ = "device"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    id_rust: Mapped[str] = mapped_column()
    pass_rust: Mapped[str] = mapped_column()
    last_screenshot_path: Mapped[str] = mapped_column()
    is_online: Mapped[bool] = mapped_column(default=True, index=True)
    heartbeat_timestamp: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    device_group_id: Mapped[Optional["DeviceGroup"] | None] = mapped_column(ForeignKey("device_group.id")) 
    device_group: Mapped[Optional["DeviceGroup"] | None] = relationship("DeviceGroup", back_populates="devices")

class Tenant(Base, AuditMixin):
    __tablename__ = "tenant"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    device_groups: Mapped[list["DeviceGroup"]] = relationship("DeviceGroup", back_populates="tenant")
