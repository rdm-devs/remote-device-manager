from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from ..database import Base
from ..audit_mixin import AuditMixin


class AuthRefreshToken(Base, AuditMixin):
    __tablename__ = "auth_refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    refresh_token: Mapped[str] = mapped_column() 
    expires_at: Mapped[datetime] = mapped_column()
    valid: Mapped[bool] = mapped_column(default=True)