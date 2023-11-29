from src.schemas import UserGroupWithUsers, UserWithUserGroups
from sqlalchemy.orm import Session
from . import schemas, models, exceptions
from ..device_group.service import check_device_group_exists
from ..user.models import User
from ..user.service import check_user_exists


def check_user_group_exists(db: Session, user_group_id: int):
    user_group = (
        db.query(models.UserGroup).filter(models.UserGroup.id == user_group_id).first()
    )
    if not user_group:
        raise exceptions.UserGroupNotFoundError()


def check_user_group_name_exists(db: Session, name: str):
    if len(name.strip()) == 0:
        raise exceptions.UserGroupInvalidNameError()

    user_group = (
        db.query(models.UserGroup).filter(models.UserGroup.name == name).first()
    )
    if user_group:
        raise exceptions.UserGroupNameTakenError()


def check_user_group_name_taken(db: Session, user_group_id: int, name: str):
    user_group = (
        db.query(models.UserGroup)
        .filter(models.UserGroup.name == name, models.UserGroup.id != user_group_id)
        .first()
    )
    if user_group:
        raise exceptions.UserGroupNameTakenError()


def get_user_group(db: Session, user_group_id: int):
    user_group = (
        db.query(models.UserGroup).filter(models.UserGroup.id == user_group_id).first()
    )
    if not user_group:
        raise exceptions.UserGroupNotFoundError()
    return user_group


def get_user_groups(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.UserGroup).offset(skip).limit(limit).all()


def get_user_group_by_name(db: Session, name: str):
    user_group = (
        db.query(models.UserGroup).filter(models.UserGroup.name == name).first()
    )
    if not user_group:
        raise exceptions.UserGroupNotFoundError
    return user_group


def create_user_group(db: Session, user_group: schemas.UserGroupCreate):
    # sanity checks:
    check_user_group_name_exists(db, user_group.name)
    if user_group.device_group_id:
        check_device_group_exists(db, user_group.device_group_id)

    db_user_group = models.UserGroup(**user_group.model_dump())
    db.add(db_user_group)
    db.commit()
    db.refresh(db_user_group)
    return db_user_group


def update_user_group(
    db: Session,
    db_user_group: UserGroupWithUsers,
    updated_user_group: schemas.UserGroupUpdate,
):
    check_user_group_exists(db, db_user_group.id)
    update_values = updated_user_group.model_dump()

    # sanity checks:
    if updated_user_group.device_group_id:
        check_device_group_exists(db, updated_user_group.device_group_id)
    else:
        # we pop "device_group_id" as the object "device_group_id" attribute will not change its value.
        update_values.pop("device_group_id")

    if len(updated_user_group.name.strip()) > 0:
        # "name" attribute is optional. Check that the new one is not taken by other user group
        check_user_group_name_taken(db, db_user_group.id, updated_user_group.name)
    else:
        # we pop "name" as the object "name" attribute will not change its value.
        update_values.pop("name")

    updated_db_user_group = (
        db.query(models.UserGroup)
        .filter(models.UserGroup.id == db_user_group.id)
        .update(values=update_values)
    )

    db.commit()
    db.refresh(db_user_group)
    return db_user_group


def delete_user_group(db: Session, db_user_group: UserGroupWithUsers):
    # sanity check
    check_user_group_exists(db, db_user_group.id)

    db.delete(db_user_group)
    db.commit()
    return db_user_group.id


def add_users(
    db: Session, db_user_group: UserGroupWithUsers, users: list[UserWithUserGroups]
):
    import pdb

    # pdb.set_trace()
    for user in users:
        check_user_exists(db, user.id)
        is_already_related = (
            db.query(models.user_and_groups_table)
            .filter(models.user_and_groups_table.columns.user_id == user.id)
            .filter(models.user_and_groups_table.columns.group_id == db_user_group.id)
            .first()
        )
        if not is_already_related:
            db_user = db.query(User).filter(User.id == user.id).first()
            db_user_group.users.append(db_user)

    db.add(db_user_group)
    db.commit()
    db.refresh(db_user_group)

    return db_user_group


def delete_users(
    db: Session,
    db_user_group: UserGroupWithUsers,
    users_to_delete: list[UserWithUserGroups],
):
    users_to_delete_copy = users_to_delete.copy()
    for user_to_delete in users_to_delete_copy:
        db_user = db.query(User).filter(User.id == user_to_delete.id).first()
        db_user_group.users.remove(db_user)

    db.commit()
    db.refresh(db_user_group)
    return db_user_group


def get_users_from_group(db: Session, user_group_id: int):
    user_group = get_user_group(db, user_group_id)
    return user_group.users
