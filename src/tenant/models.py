from sqlalchemy import ForeignKey, Table, Column, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import List
from ..database import Base
from ..audit_mixin import AuditMixin
from ..entity.models import Entity


tenants_and_users_table = Table(
    "tenants_and_users",
    Base.metadata,
    Column("tenant_id", ForeignKey("tenant.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
)


class Tenant(Base, AuditMixin):
    __tablename__ = "tenant"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True)
    entity_id: Mapped[int] = mapped_column(ForeignKey(Entity.id))
    folders: Mapped[List["src.folders.models.Folder"]] = relationship(
        "Folder", back_populates="tenant"
    )
    users: Mapped[List["src.user.models.User"]] = relationship(
        secondary=tenants_and_users_table, back_populates="tenants"
    )
    entity: Mapped[Entity] = relationship(Entity)
    tags: Mapped[List["src.tag.models.Tag"]] = relationship(
        "src.tag.models.Tag", back_populates="tenant"
    )

    def add_tag(self, tag: "src.tag.models.Tag") -> None:
        self.tags.append(tag)
