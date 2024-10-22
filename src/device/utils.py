from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Union, Optional
from src.device import models


def get_device_by_serialno(
    db: Session, serialno: Optional[str] = None
) -> Union[models.Device | None]:
    stmt = select(models.Device).where(models.Device.serialno == serialno)
    return None if serialno is None else db.scalars(stmt).first()
