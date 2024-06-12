from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.sql import func
from typing import Optional, List
from ..database import Base
from ..audit_mixin import AuditMixin
from ..entity.models import Entity
from ..role.models import Role
from ..tenant.models import tenants_and_users_table


class User(Base, AuditMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    disabled: Mapped[bool] = mapped_column(default=False)
    hashed_password: Mapped[str] = mapped_column()
    last_login: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )
    entity_id: Mapped[int] = mapped_column(ForeignKey(Entity.id))
    entity: Mapped["src.entity.models.Entity"] = relationship(
        "src.entity.models.Entity", foreign_keys=entity_id
    )
    role_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Role.id))
    role: Mapped[Optional[Role]] = relationship(Role, foreign_keys="User.role_id")
    tenants: Mapped[List["src.tenant.models.Tenant"]] = relationship(
        secondary=tenants_and_users_table, back_populates="users"
    )

    @property
    def is_admin(self):
        return self.role_id == 1

    @property
    def tags(self):
        return self.entity.tags

    def add_tenant(self, tenant: "src.tenant.models.Tenant") -> None:
        self.tenants.append(tenant)

    def add_tag(self, tag: "src.tag.models.Tag") -> None:
        self.tags.append(tag)

    def get_tenants_ids(self) -> List[int]:
        return [t.id for t in self.tenants]

    def get_folder_tree(self) -> List["src.folder.models.Folder"]:
        folders = []
        for t in self.tenants:
            folders.extend([f for f in t.folders if f.parent_id is None])
        return folders

    def get_folder_tree_ids(self) -> List[int]:
        folders = self.get_folder_tree()
        return [f.id for f in folders]

    def get_device_ids(self) -> List[int]:
        folders = []
        device_ids = []
        for t in self.tenants:
            folders.extend([f for f in t.folders])
        for f in folders:
            device_ids.extend([d.id for d in f.devices])
        return device_ids

    @property
    def role_name(self):
        return self.role.name