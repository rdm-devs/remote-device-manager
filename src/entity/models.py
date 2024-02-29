from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import List
from ..database import Base
from ..audit_mixin import AuditMixin
from ..tag.models import entities_and_tags_table


class Entity(Base, AuditMixin):
    __tablename__ = "entity"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    # uuid: Mapped[str] = mapped_column(index=True)
    # para manejo de uuid como dato "nativo" ver:
    #   1- https://stackoverflow.com/questions/183042/how-can-i-use-uuids-in-sqlalchemy
    #   2- https://fastapi-utils.davidmontague.xyz/user-guide/basics/guid-type/
    tags: Mapped[List["src.tag.models.Tag"]] = relationship(
        secondary=entities_and_tags_table, back_populates="entities"
    )
