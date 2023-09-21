# original author: https://gist.github.com/techniq/5174410

from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func

class AuditMixin():
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    @declared_attr
    def created_by_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey('user.id', name='fk_%s_created_by_id' % cls.__name__, use_alter=True),
            # nullable=False,
            default=None # TODO: replace with get_current_user kinda function
        )

    @declared_attr
    def created_by(cls) -> Mapped["User"]:
        return relationship(
            primaryjoin='User.id == %s.created_by_id' % cls.__name__,
            remote_side='User.id'
        )

    @declared_attr
    def updated_by_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey('user.id', name='fk_%s_updated_by_id' % cls.__name__, use_alter=True),
            # nullable=False,
            default=None, # TODO: replace with get_current_user kinda function
            onupdate=None # TODO: replace with get_current_user kinda function
        )

    @declared_attr
    def updated_by(cls) -> Mapped["User"]:
        return relationship(
            primaryjoin='User.id == %s.updated_by_id' % cls.__name__,
            remote_side='User.id'
        )
