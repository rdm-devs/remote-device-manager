# original author: https://gist.github.com/techniq/5174410
import contextvars
from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func

_auth_user_ctx = contextvars.ContextVar("auth_user_ctx", default=None)


def get_auth_user() -> int:
    return _auth_user_ctx.get()


class AuditMixin:
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(), onupdate=func.now()
    )

    @declared_attr
    def created_by_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey(
                "user.id", name="fk_%s_created_by_id" % cls.__name__, use_alter=True
            ),
            nullable=True,
        )

    @declared_attr
    def created_by(cls) -> Mapped["User"]:
        return relationship(
            primaryjoin="User.id == %s.created_by_id" % cls.__name__,
            remote_side="User.id",
        )

    @declared_attr
    def updated_by_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey(
                "user.id", name="fk_%s_updated_by_id" % cls.__name__, use_alter=True
            ),
            onupdate=get_auth_user(),  # TODO: replace with get_current_user kinda function
            nullable=True,
        )

    @declared_attr
    def updated_by(cls) -> Mapped["User"]:
        return relationship(
            primaryjoin="User.id == %s.updated_by_id" % cls.__name__,
            remote_side="User.id",
        )

    # Override __init__ to set created_by_id and updated_by_id
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_user_id = get_auth_user()
        if current_user_id is not None:
            self.created_by_id = current_user_id
            self.updated_by_id = current_user_id
