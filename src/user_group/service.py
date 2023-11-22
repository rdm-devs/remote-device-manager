from src.schemas import UserGroupWithUsers
from sqlalchemy.orm import Session
from . import schemas, models


def get_user_group(db: Session, group_id: int):
    return db.query(models.UserGroup).filter(models.UserGroup.id == group_id).first()


def get_user_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UserGroup).offset(skip).limit(limit).all()


def get_user_group_by_name(db: Session, name: str):
    return db.query(models.UserGroup).filter(models.UserGroup.name == name).first()


def create_user_group(db: Session, user_group: schemas.UserGroupCreate):
    db_user_group = models.UserGroup(name=user_group.name)
    db.add(db_user_group)
    db.commit()
    db.refresh(db_user_group)
    return db_user_group


def update_user_group(
    db: Session,
    db_user_group: UserGroupWithUsers,
    updated_user_group: schemas.UserGroupUpdate,
):
    updated_db_user_group = (
        db.query(models.UserGroup)
        .filter(models.UserGroup.id == db_user_group.id)
        .update(values=updated_user_group.model_dump())
    )

    db.commit()
    db.refresh(db_user_group)
    return db_user_group


def delete_user_group(db: Session, db_user_group: UserGroupWithUsers):
    db.delete(db_user_group)
    db.commit()
    return db_user_group.id
