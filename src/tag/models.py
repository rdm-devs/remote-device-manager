from sqlalchemy import ForeignKey, Table, Column, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List, Optional
from enum import StrEnum, auto
from src.database import Base
from src.audit_mixin import AuditMixin


class Type(StrEnum):
    DEVICE = auto()
    FOLDER = auto()
    TENANT = auto()
    USER = auto()
    GLOBAL = auto()
    USER_CREATED = auto()


entities_and_tags_table = Table(
    "entities_and_tags",
    Base.metadata,
    Column(
        "entity_id",
        ForeignKey("entity.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
)


class Tag(AuditMixin, Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(255), index=True
    )  # e.g.: os-android-9 | brand-xiaomi
    entities: Mapped[List["src.entity.models.Entity"]] = relationship(
        secondary=entities_and_tags_table, back_populates="tags"
    )
    tenant_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tenant.id", ondelete="CASCADE"), nullable=True
    )
    tenant: Mapped[Optional["src.tenant.models.Tenant"]] = relationship(
        "src.tenant.models.Tenant", back_populates="tags_for_tenant", cascade="all, delete"
    )
    type: Mapped[Type]
