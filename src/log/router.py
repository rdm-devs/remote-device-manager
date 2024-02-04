from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from . import service, schemas

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/{user_id}", response_model=schemas.LogEntry)
def read_logs_from_user(user_id: int, db: Session = Depends(get_db)):
    db_log_entry = service.get_log_entries_from_user(db, user_id=user_id)
    return db_log_entry


@router.get("/", response_model=list[schemas.LogEntry])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_logs(db, skip=skip, limit=limit)
