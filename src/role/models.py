from sqlalchemy.orm import mapped_column, Mapped
from ..database import Base

class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)