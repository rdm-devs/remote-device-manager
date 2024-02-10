from sqlalchemy.orm import mapped_column, Mapped
from ..database import Base
from ..audit_mixin import AuditMixin


class Role(Base, AuditMixin):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
