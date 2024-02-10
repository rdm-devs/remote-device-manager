from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional
from ..database import Base
from ..audit_mixin import AuditMixin
from ..entity.models import Entity
from ..role.models import Role
from ..tenant.models import tenants_and_users_table


class User(Base, AuditMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    last_login: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )
    entity_id: Mapped[int] = mapped_column(ForeignKey(Entity.id))
    role_id: Mapped[int] = mapped_column(ForeignKey(Role.id))
    tenants: Mapped[list["src.tenant.models.Tenant"]] = relationship(
        secondary=tenants_and_users_table, back_populates="users"
    )
