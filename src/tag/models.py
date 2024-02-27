from sqlalchemy import ForeignKey, Table, Column, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from ..database import Base
from ..audit_mixin import AuditMixin

entities_and_tags_table = Table(
    "entities_and_tags",
    Base.metadata,
    Column("entity_id", ForeignKey("entity.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
    Column("created_at", DateTime, default=func.now()),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now()),
)


class Tag(Base, AuditMixin):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True, unique=True) #e.g.: os-android-9 | brand-xiaomi
    entities: Mapped[list["src.entity.models.Entity"]] = relationship(
        secondary=entities_and_tags_table, back_populates="tags"
    )
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenant.id"))
