from datetime import datetime
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import mapped_column, Mapped
from ..database import Base
from ..audit_mixin import AuditMixin


class AuthRefreshToken(AuditMixin, Base):
    __tablename__ = "auth_refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    serial_number: Mapped[str] = mapped_column(String(1000), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(1000))
    expires_at: Mapped[datetime] = mapped_column()
    valid: Mapped[bool] = mapped_column(default=True)


class AuthPasswordRecoveryToken(AuditMixin, Base):
    __tablename__ = "auth_password_recovery_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(1000))
    recovery_token: Mapped[str] = mapped_column(String(1000))
    expires_at: Mapped[datetime] = mapped_column()
