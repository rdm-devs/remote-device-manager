from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped
from src.database import Base
from src.audit_mixin import AuditMixin


class Role(AuditMixin, Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
