from pydantic import ValidationError
from sqlalchemy.orm import Session
from src.tenant.service import check_tenant_exists
from src.log.exceptions import (
    LogEntryNotFoundError,
)
from . import schemas, models


def create_log_entry(db: Session, log_entry: schemas.LogEntryCreate):
    db_log_entry = models.LogEntry(**log_entry.model_dump())
    db.add(db_log_entry)
    db.commit()
    db.refresh(db_log_entry)
    return db_log_entry


def get_log_entry(db: Session, log_entry_id: int):
    db_log_entry = (
        db.query(models.LogEntry).filter(models.LogEntry.id == log_entry_id).first()
    )
    if db_log_entry is None:
        raise exceptions.LogEntryNotFoundError()
    return db_log_entry


def get_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.LogEntry).offset(skip).limit(limit).all()


def get_log_entries_from_user(
    db: Session, user_id: id, skip: int = 0, limit: int = 100
):
    return (
        db.query(models.LogEntry)
        .filter(models.LogEntry.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_log_entry(db: Session, log_entry_id: int):
    # sanity check
    db_log_entry = (
        db.query(models.LogEntry).filter(models.LogEntry.id == log_entry_id).first()
    )

    db.delete(db_log_entry)
    db.commit()
    return db_log_entry.id
